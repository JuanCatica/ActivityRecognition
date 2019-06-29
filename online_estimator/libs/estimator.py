from collections import deque
import pandas as pd
import numpy as np

class online_estimator():
    
    def __init__(self, estimator, scaler, metrics, signal_columns, win_size_segment_ms, overlap, frec):
        self.estimator = estimator
        self.scaler = scaler
        self.metrics = metrics
        self.signal_columns = signal_columns
        self.features_names = []
        for metric in metrics:
            self.features_names += [str(col) + '_' + metric for col in signal_columns]
        self.df_features = pd.DataFrame(columns=self.features_names)
        self.win_size_segment_ms = win_size_segment_ms
        self.overlap = overlap
        
        self.overlap_cnts = int(self.overlap*self.win_size_segment_ms * frec / 1000.0)
        self.win_size_segment_cnts = int(self.win_size_segment_ms * frec / 1000.0)
        
        self.label = 0
        self.buffer = deque()
        self.counter = 0
    
    def add_register(self, data):
        if len(data) == len(self.signal_columns):
            self.buffer.append(data)
            self.counter += 1
            
            if self.counter >= self.overlap_cnts:
                self.predict()
                self.counter = 0
            
            if len(self.buffer) >= self.win_size_segment_cnts:
                self.buffer.popleft() 
        else:
            print("Error en los datos",len(data),len(self.signal_columns))
    
    def get_label(self):
        return self.label
    
    def get_buffer(self):
        return self.buffer
    
    def predict(self):
        df_test = pd.DataFrame(list(self.buffer), columns= self.signal_columns)
        df_test = df_test.fillna(method='ffill')
        features = self.fast_extract_window_features(df_test,self.metrics)
        self.df_features.loc[0] = features
        X = self.scaler.transform(self.df_features)
        self.label = self.estimator.predict(X)[0]
        return self.label
    
    def get_metrics(self, df, method):
        if method == "median":
            return df.median()
        if method == "mean":
            return df.mean()
        if method == "std":
            return df.std()
        if method == "skew":
            return df.skew()
        if method == "var":
            return df.var()
        if method == "max":
            return df.max()
        if method == "min":
            return df.min()
        if method == "kurt":
            return df.kurt()
        print("unknown function !")
        return None

    def fast_extract_window_features(self, df_signals, features):
        lista_metris = []
        for metric in features:
            df_metric = self.get_metrics(df_signals, metric)
            df_metric.index = [str(col) + '_' + metric for col in df_metric.index]
            lista_metris.append(df_metric)
        return pd.concat(lista_metris)

