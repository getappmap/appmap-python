import numpy as np

class ExampleNumpyClass:
    def __init__(self, values):
        self.values = np.array(values, dtype=np.int64)

    def get_values(self):
        return self.values

    def sum_values(self):
        return np.sum(self.get_values()).astype(np.int64)

    @staticmethod
    def print_result(result: np.int64):
        print(f"The sum of the values is: {result} (type: {type(result)})")

    @staticmethod
    def go():
        values = [1, 2, 3, 4, 5]
        simple_class = ExampleNumpyClass(values)
        result = simple_class.sum_values()
        ExampleNumpyClass.print_result(result)
