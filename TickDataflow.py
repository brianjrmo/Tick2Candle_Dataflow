import datetime
import logging
import json
import pandas as pd
import apache_beam as beam
from apache_beam import window
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.options.pipeline_options import StandardOptions

pipeline_options = PipelineOptions()
pipeline_options.view_as(SetupOptions).save_main_session = True
pipeline_options.view_as(StandardOptions).streaming = True

SAMPLE_PERIOD_SEC = 60 * 60 
BIGQUERY_TABLE    = 'etl-practice-283400:beamlab.fxdb'
TEMP_LOCATION     = 'gs://etl-practice-283400/tmp'
SUBSCRIPTIONS     = 'projects/etl-practice-283400/subscriptions/forex_tick_sub'

# add TickTime as event grouping time
def add_timestamp(data):
    tick_time        = datetime.datetime.strptime(data['TickTime'][0:19],'%Y.%m.%d %H:%M:%S')
    tick_timestamp   = datetime.datetime.timestamp(tick_time)
    event_timestamp  = tick_timestamp // SAMPLE_PERIOD_SEC * SAMPLE_PERIOD_SEC + SAMPLE_PERIOD_SEC
    data['TickTime'] = pd.to_datetime(data['TickTime'],format='%Y.%m.%d %H:%M:%S.%f')
    data['EvenTime'] = format(datetime.datetime.fromtimestamp(event_timestamp),'%Y-%m-%d %H:%M:%S')
    return beam.window.TimestampedValue(data, event_timestamp)

class ParCandle(beam.DoFn):
    def __init__(self):
        beam.DoFn.__init__(self)
    
    def process(self, elem):
        df = pd.DataFrame(elem[1])
        symbol      = df.loc[df.index[0],['Symbol']][0]
        time        = df.loc[df.index[0],['EvenTime']][0]
        open_price  = df.loc[df.index[0],['Price']][0]
        close_price = df.loc[df.index[-1],['Price']][0]
        high_price  = df.Price.max()
        low_price   = df.Price.min()
        volume      = df.Volume.sum()
        record_in_dict = [{'datetime' : time,
                           'symbol'   : symbol,
                           'open'     : open_price,
                           'close'    : close_price,
                           'high'     : high_price,
                           'low'      : low_price,
                           'volume'   : float(volume)}]
        return record_in_dict

logging.getLogger().setLevel(logging.INFO)
with beam.Pipeline(options=pipeline_options) as p:
  messages = (
      p
      | beam.io.ReadFromPubSub(subscription=SUBSCRIPTIONS).with_output_types(bytes)
      | 'decode'    >> beam.Map(lambda x: x.decode('utf-8'))
      | 'ticking'   >> beam.FlatMap(lambda x: json.loads(x))
      | 'timestamp' >> beam.Map(add_timestamp)
      | 'Window'    >> beam.WindowInto(window.FixedWindows(SAMPLE_PERIOD_SEC))
      | 'Key Value' >> beam.Map(lambda x: (x['Symbol'],x))
      | 'max price' >> beam.GroupByKey()
      | 'statistic' >> beam.ParDo(ParCandle())
      | 'display'   >> beam.io.WriteToBigQuery(BIGQUERY_TABLE,
                                               custom_gcs_temp_location=TEMP_LOCATION,
                                               write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
  )
