from e2e_mlops_demo.common import Task

import openml
from typing import Optional
from pyspark.sql import DataFrame as SparkDataFrame


class DatasetLoaderTask(Task):
    def get_data(self, limit: Optional[int] = None) -> SparkDataFrame:
        self.logger.info("Loading the dataset")
        dataset = openml.datasets.get_dataset("CreditCardFraudDetection")
        X, y, _, _ = dataset.get_data(dataset_format="dataframe")
        _df = X
        # sanitize column names
        _df.rename(columns={"Class": "TARGET"})
        _df.columns = [c.lower() for c in _df]
        # limit data for testing purposes
        if limit:
            _df = _df.head(limit)
        self.logger.info("Loading the dataset - done")
        _spark_df = self.spark.createDataFrame(_df)
        return _spark_df

    def prepare_database(self):
        db_name = self.conf["output"]["database"]

        if not db_name in [d.name for d in self.spark.catalog.listDatabases()]:
            self.logger.info(f"Database {db_name} doesn't exist, creating it")
            self.spark.sql(f"CREATE DATABASE {db_name}")
            self.logger.info("Database has been created")

    def get_output_table_name(self) -> str:
        output_conf = self.conf["output"]
        return f"{output_conf['database']}.{output_conf['table']}"

    def save_data(self, sdf: SparkDataFrame):
        full_table_name = self.get_output_table_name()
        self.logger.info(
            f"Saving data to {full_table_name}. Existing data will be overwritten"
        )
        sdf.write.format("delta").mode("overwrite").saveAsTable(full_table_name)
        self.logger.info("Data saved successfully!")

    def launch(self):
        self.prepare_database()
        _df = self.get_data(self.conf.get("limit"))
        self.save_data(_df)


def entrypoint():  # pragma: no cover
    task = DatasetLoaderTask()
    task.launch()


# if you're using spark_python_task, you'll need the __main__ block to start the code execution
if __name__ == "__main__":
    entrypoint()