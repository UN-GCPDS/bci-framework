from bci_framework.extensions.data_analysis import DataAnalysis

class Analysis(DataAnalysis):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

if __name__ == '__main__':
    Analysis()
    
