class Dataset:
    """Represents a data science dataset in the platform."""

    def __init__(
        self,
        dataset_id: int,
        name: str,
        category: str,
        source: str,
        last_updated: str,
        record_count: int,
        file_size_mb: float
    ):
        self.__id = dataset_id
        self.__name = name
        self.__category = category
        self.__source = source
        self.__last_updated = last_updated
        self.__record_count = record_count
        self.__file_size_mb = file_size_mb

    def get_id(self) -> int:
        """Return the dataset ID."""
        return self.__id

    def get_name(self) -> str:
        """Return the dataset name."""
        return self.__name

    def get_category(self) -> str:
        """Return the dataset category."""
        return self.__category

    def get_source(self) -> str:
        """Return the data source."""
        return self.__source

    def get_last_updated(self) -> str:
        """Return the last updated date."""
        return self.__last_updated

    def get_record_count(self) -> int:
        """Return the number of records."""
        return self.__record_count

    def get_file_size_mb(self) -> float:
        """Return the file size in MB."""
        return self.__file_size_mb

    def calculate_size_gb(self) -> float:
        """Calculate and return size in GB."""
        return self.__file_size_mb / 1024

    def get_record_density(self) -> float:
        """
        Calculate records per MB.

        Returns:
            float: Records per MB, or 0 if size is 0
        """
        if self.__file_size_mb > 0:
            return self.__record_count / self.__file_size_mb
        return 0.0

    def is_large_dataset(self, threshold_mb: float = 100.0) -> bool:
        """
        Check if dataset exceeds a size threshold.

        Args:
            threshold_mb: Size threshold in MB (default 100)

        Returns:
            bool: True if dataset is larger than threshold
        """
        return self.__file_size_mb > threshold_mb

    def __str__(self) -> str:
        return f"Dataset {self.__id}: {self.__name} ({self.__file_size_mb:.2f} MB, {self.__record_count:,} records)"

    def __repr__(self) -> str:
        return self.__str__()
