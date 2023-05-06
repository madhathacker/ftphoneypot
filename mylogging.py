import logging

logging.basicConfig(
    filename="ftphp.log", 
    level=logging.INFO, 
    format = "%(asctime)s %(levelname)s: %(message)s", 
    datefmt = "%d.%m.%Y %H:%M:%S")

logging.root.setLevel(logging.INFO)

class FileWriter():
	def __init__(self, filename):
		self.filename = filename
		
	def append(self, line):
		with open(self.filename, "a") as outfile:
			outfile.write(str(line))
			outfile.write("\n")

class HandlerManager():
	def __init__(self, config):
		self.enabled_handlers = config.enabled_handlers
		""" if self.enabled_handlers['elasticsearch']:
			self.es_client = ElasticsearchClient(
				config.elasticsearch['host'], 
				config.elasticsearch['port'], 
				config.elasticsearch['index']
			)
			log.info("Saving to Elasticsearch enabled. Destination: http://%s:%s/%s" % (
				config.elasticsearch['host'], 
				config.elasticsearch['port'], 
				config.elasticsearch['index']
			)) """
		if self.enabled_handlers['file']:
			self.file_writer = FileWriter(config.filename)
			log.info("Saving to File enabled. Filename: %s" % config.filename)
		if self.enabled_handlers['screen']:
			log.info("Output to Screen (STDOUT) enabled.")
		
	def handle(self, element, type='intrusion'):
		if self.enabled_handlers['elasticsearch']:
			self.es_client.saveOne(element, type)
		if self.enabled_handlers['file']:
			self.file_writer.append(element)
		if self.enabled_handlers['screen']:
			log.warning(element)