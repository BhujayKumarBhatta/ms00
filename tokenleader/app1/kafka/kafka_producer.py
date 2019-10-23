from kafka import KafkaProducer
from kafka.errors import KafkaError
from json import  dumps


def preparekafkaresponse(wfc, msg_source, msg_body):        
    kafka_response = {"request_id": wfc.request_id,
                      "wfcdict": wfc.to_dict(),
                      "msg_source": msg_source,
                      "msg_body": msg_body}

    return   kafka_response


def notify_kafka(conf, wfc, topic, kafka_response):
    resp = {}
    #conf = conf.yml
    ''' within the consumer itself this method produce  the processed resutl to kafka'''
    producer = KafkaProducer(bootstrap_servers=conf.get('kafka_servers'),
                      value_serializer=lambda x: 
                      dumps(x).encode('utf-8'))
 
#     kafka_response.pop('_id')
    future = producer.send(topic, value= kafka_response)
    # Block for 'synchronous' sends
    try:
        record_metadata = future.get(timeout=10)
        # Successful result returns assigned partition and offset
        resp = {"request_id": wfc.request_id, 
                "save_status": ("posted , status will be mailed or can be checked "
                                "after some time against the request id")}
        print('...................',record_metadata.topic, 
              record_metadata.partition,
              record_metadata.offset,
              'Produced for telegraph')
        print(kafka_response)      
    except KafkaError:
        # Decide what to do if produce request failed...
        #log.exception()
        print('failed to produce')           
        resp = {"request_id": wfc.request_id, 
                "save_status": ("posting failed , system err, try again later")}
    return resp
        
