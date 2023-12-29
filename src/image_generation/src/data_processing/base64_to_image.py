import base64
import io

from PIL import Image
from pyspark.sql.functions import explode
from pyspark.sql.functions import col, expr
from pyspark.sql import SparkSession


def convert_base64_to_image(df):
    img = Image.open(io.BytesIO(base64.decodebytes(bytes(df.image, "utf-8"))))
    image_location = f"/opt/ml/processing/output/Apple___Cedar_apple_rust/cedar_apple_rust_{df.uuid}.jpeg"
    img.save(image_location)


if __name__ == "__main__":
    spark = SparkSession.builder.appName("PySparkApp").getOrCreate()
    df = spark.read.json('/opt/ml/processing/input/Apple___Cedar_apple_rust/')
    df = df.select(col('prompt'), explode(col('generated_images')).alias('image'))
    df = df.withColumn("uuid", expr("uuid()"))

    df.foreach(convert_base64_to_image)


