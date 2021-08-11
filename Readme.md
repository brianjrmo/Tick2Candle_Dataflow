# Tick2Candle_Dataflow
<h2>This project demo how to convert tick data to candle data by using dataflow in Google Cloud Platform.</h2>
<p>Flow: Tick Data(raw) --> GCP Pub/Sub --> GCP Dataflow --> GCP BigQuery</p>
<h2>Three components:</h2>
<h4>1. Generate tick data</h4>
   This part mimic the gernation of tick data by using Metatrader 4(MT4) platform. It will generate csv file with format in 1.3. Other source of tick data also good, as long as comply with output.<br>

<ul>
<li>
1.1 MT4<br>
    To download and install MT4 from:<br>
    https://www.fxcm.com/ca/platforms/metatrader-4/download/<br>
</li>
<li>
1.2 Expert:<br>
    <a href="https://github.com/brianjrmo/Tick2Candle_Dataflow/blob/main/mt4/ticking.mq4">mt4/ticking.mq4</a><br>
</li>
<li>
1.3 Output:<br>
    Field name    format<br>
    TickTime      yyyy.mm.dd HH:MM.SS.FFFFFFFFF<br>
    Symbol        6 characters currency pair<br>
    Price         decimal<br>
    Volume        integer<br>
    example: <a href="https://github.com/brianjrmo/Tick2Candle_Dataflow/blob/main/mt4/Sample_Tick.csv">mt4/Sample_Tick.csv</a><br>
</li>
</ul>
<br>
<h4>2. Publish to GCP Pubsub</h4>
   Python script to publish tick data to google pubsub. A windows schedule job will trigger the python script every 2 minutes<br>
   Python script to publish tick data: <a href="https://github.com/brianjrmo/Tick2Candle_Dataflow/blob/main/publish/TickToPubsub.py">publish/TickToPubsub.py</a><br>
   Windows batch job run by schedule: <a href="https://github.com/brianjrmo/Tick2Candle_Dataflow/blob/main/publish/TickToPubsub.bat">publish/TickToPubsub.bat</a><br>


<h4>3. Capture Pubsub message to Dataflow</h4>
   Subscript google pubsub and convert tick data to hourly candle. It will run in google dataflow.<br>
   Write Candle data to BigQuery table.<br>
   Dataflow script in python: <a href="https://github.com/brianjrmo/Tick2Candle_Dataflow/blob/main/TickDataflow.py">TickDataflow.py</a><br>
   Dataflow start from GCP terminal  with this command:<br>
   python TickDataflow.py  --runner DataflowRunner --project etl-practice-283400 --region us-west1 --streaming<br>
   <a href="https://github.com/brianjrmo/Tick2Candle_Dataflow/blob/main/BigQuery_result.JPG">BigQuery table: fxdb</a>
   

