# https://debuggercafe.com/plantvillage-dataset-disease-recognition-using-pytorch/
# https://debuggercafe.com/plantdoc-plant-disease-recognition/
import torch
import argparse
import torch.nn as nn
import torch.optim as optim
import os
import logging
from tqdm.auto import tqdm

from datasets import get_datasets, get_data_loaders
from model import build_model
from utils import save_model

seed = 42
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = True
import mlflow

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)

# Construct the argument parser.
parser = argparse.ArgumentParser()

# hyperparameters sent by the client are passed as command-line arguments to the script.
parser.add_argument(
    '-e', '--epochs',
    type=int,
    default=10,
    help='Number of epochs to training our network for'
)
parser.add_argument(
    '-lr', '--learning-rate',
    type=float,
    dest='learning_rate',
    default=0.001,
    help='Learning rate for training the model'
)

parser.add_argument(
    '-momentum', '--momentum',
    type=float,
    dest='momentum',
    default=0.9,
    help='Momentum for training the model'
)

parser.add_argument(
    '-tracking_uri', '--tracking_uri',
    type=str,
    dest='tracking_uri',
    default=0.9,
    help='MLflow tracking server uri'
)

parser.add_argument(
    '-m', '--model',
    type=str,
    default='mobilenetv3_large',
    help='model name',
    choices=['mobilenetv3_large', 'shufflenetv2_x1_5', 'efficientnetb0']
)

# input data and model directories
parser.add_argument(
    '--model-dir',
    type=str,
    default=os.environ['SM_MODEL_DIR'])
parser.add_argument(
    '--training',
    type=str,
    default=os.environ['SM_CHANNEL_TRAINING'])
parser.add_argument(
    '--test',
    type=str,
    default=os.environ['SM_CHANNEL_TESTING'])
args = vars(parser.parse_args())


# Training function.
def train(model, trainloader, optimizer, criterion, device):
    model.train()
    logging.info('Training')
    train_running_loss = 0.0
    train_running_correct = 0
    counter = 0
    for batch_no, data in tqdm(enumerate(trainloader), total=len(trainloader)):
        counter += 1
        image, labels = data
        image = image.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        # Forward pass.
        outputs = model(image)
        # Calculate the loss.
        loss = criterion(outputs, labels)
        train_running_loss += loss.item()
        # Calculate the accuracy.
        _, preds = torch.max(outputs.data, 1)
        train_running_correct += (preds == labels).sum().item()
        # Backpropagation.
        loss.backward()
        # Update the weights.
        optimizer.step()

    # Loss and accuracy for the complete epoch.
    epoch_loss = train_running_loss / counter
    epoch_acc = 100. * (train_running_correct / len(trainloader.dataset))
    return epoch_loss, epoch_acc


# Validation function.
def validate(model, testloader, criterion, device):
    model.eval()
    logging.info('Validation')
    valid_running_loss = 0.0
    valid_running_correct = 0
    counter = 0

    with torch.no_grad():
        for i, data in tqdm(enumerate(testloader), total=len(testloader)):
            counter += 1

            image, labels = data
            image = image.to(device)
            labels = labels.to(device)
            # Forward pass.
            outputs = model(image)
            # Calculate the loss.
            loss = criterion(outputs, labels)
            valid_running_loss += loss.item()
            # Calculate the accuracy.
            _, preds = torch.max(outputs.data, 1)
            valid_running_correct += (preds == labels).sum().item()

    # Loss and accuracy for the complete epoch.
    epoch_loss = valid_running_loss / counter
    epoch_acc = 100. * (valid_running_correct / len(testloader.dataset))
    return epoch_loss, epoch_acc


def main():
    out_dir = args['model_dir']

    # Load the training and validation datasets.
    dataset_train, dataset_valid, dataset_classes = get_datasets(data_dir=args['training'])
    # Load the training and validation data loaders.
    train_loader, valid_loader = get_data_loaders(dataset_train, dataset_valid)

    logging.info("==>>> total training batch number: {}".format(len(train_loader)))
    logging.info("==>>> total testing batch number: {}\n".format(len(valid_loader)))

    # Training parameters.
    lr = args['learning_rate']
    momentum = args['momentum']
    epochs = args['epochs']
    device = ('cuda' if torch.cuda.is_available() else 'cpu')
    batch_size = len(train_loader)

    # Load the model.
    model = build_model(
        model_name=args['model'],
        fine_tune=True,
        num_classes=len(dataset_classes)
    ).to(device)
    logging.info(model)
    logging.info("# parameters: {}".format(sum(param.numel() for param in model.parameters())))

    # Optimizer.
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)
    # Loss function.
    criterion = nn.CrossEntropyLoss()

    training_parameters = {
        "batch size": batch_size,
        "no of epochs": epochs,
        "optimizer": "stochastic gradient descent",
        "learning rate": lr,
        "momentum": momentum,
        "loss": "cross entropy",
        "data": {"synth": 0, "real": 1}
    }

    best_acc = 0.0
    best_epoch = 0
    with mlflow.start_run(experiment_id=experiment_id):
        # LOG PARAMS
        mlflow.log_params(training_parameters)

        # Start the training.
        for epoch in range(epochs):
            logging.info(f"Epoch {epoch + 1} of {epochs}")
            train_epoch_loss, train_epoch_acc = train(model, train_loader,
                                                      optimizer, criterion, device)
            valid_epoch_loss, valid_epoch_acc = validate(model, valid_loader,
                                                         criterion, device)

            # LOG METRICS
            metrics = {
                "training loss": train_epoch_loss,
                "training accuracy": train_epoch_acc,
                "validation loss": valid_epoch_loss,
                "validation accuracy": valid_epoch_acc
            }
            mlflow.log_metrics(metrics=metrics, step=epoch)

            logging.info(f"Training loss: {train_epoch_loss:.3f}, training acc: {train_epoch_acc:.3f}")
            logging.info(f"Validation loss: {valid_epoch_loss:.3f}, validation acc: {valid_epoch_acc:.3f}")
            logging.info('-' * 50)

            # early stopping with zero patience
            if valid_epoch_acc < best_acc:
                break
            else:
                best_acc = valid_epoch_acc
                best_epoch = epoch

        # LOG MODEL
        mlflow.pytorch.log_model(model, artifact_path="{}-{}".format(best_epoch, best_acc))

        # Save the trained model weights to disk
        save_model(epochs, model, optimizer, criterion, out_dir)


if __name__ == '__main__':
    mlflow.set_tracking_uri(args['tracking_uri'])
    experiment_id = mlflow.get_experiment_by_name(args['model'])
    if experiment_id is None:
        experiment_id = mlflow.create_experiment(args['model'])
    else:
        experiment_id = experiment_id.experiment_id
    main()
