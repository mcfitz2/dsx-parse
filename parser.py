

import re
import pprint
pp = pprint.PrettyPrinter(indent=4)
class Record(object):
	def __init__(self, properties):
		self.properties = properties
	def factory(self):
		if self.properties.get("stagetype", None):
			return Stage(self.properties).factory()
		elif self.properties.get("partner", None):
			return Link(self.properties).factory()
		elif self.properties.get("oletype", None) == "CAnnotation":
			return Annotation(self.properties).factory() 
		elif self.properties.get("oletype", None) == "CContainerView":
			return ContainerView(self.properties).factory()
		elif self.properties.get("oletype",None) == "CJobDefn":
			return JobDefinition(self.properties).factory()
		else:
			pp.pprint(self.properties)
class Link(Record):
	def __init__(self, properties):
		self.properties = properties
	def factory(self):
		return self
class Annotation(Record):
	def __init__(self, properties):
		self.properties = properties
	def factory(self):
		return self
class ContainerView(Record):
	def __init__(self, properties):
		self.properties = properties
	def factory(self):
		return self
class JobDefinition(Record):
	def __init__(self, properties):
		self.properties = properties
	def factory(self):
		return self
class Stage(Record):
	def __init__(self, properties):
		self.properties = properties
	def factory(self):
		if self.properties["oletype"] == "CTransformerStage":
			return TransformerStage(self.properties)
		elif self.properties["oletype"] == "CCustomStage":
			if self.properties["stagetype"] == "OracleConnectorPX":
				return OracleConnectorStage(self.properties)
			elif self.properties["stagetype"] == "PxSequentialFile":
				return SequentialFileStage(self.properties)
			elif self.properties["stagetype"] == "PxAggregator":
				return AggregatorStage(self.properties)
			elif self.properties["stagetype"] == "PxRemDup":
				return RemoveDuplicatesStage(self.properties)
			elif self.properties["stagetype"] == "PxCopy":
				return CopyStage(self.properties)
			else:
				print "Stage type not implemented"
				pp.pprint(self.properties)
		elif self.properties["oletype"] == "CJSExceptionHandler":
			return ExceptionHandlerStage(self.properties)
		elif self.properties["oletype"] == "CJSJobActivity":
			return JobActivityStage(self.properties)
		elif self.properties["oletype"] == "CJSMailActivity":
			return MailActivityStage(self.properties)
		elif self.properties["oletype"] == "CJSTerminatorActivity":
			return TerminatorActivityStage(self.properties)
		elif self.properties["oletype"] == "CJSUserVarsActivity":
			return UserVarsActivityStage(self.properties)
		#else:
			#print self.properties
	def __str__(self):
		return self.properties["name"]
	def __repr__(self):
		return self.properties["name"]
class DSX(object):
	stage_types = ['OracleConnectorPX',
					'CTransformerStage',
					'PxSequentialFile',
					'PxAggregator',
					'CJobActivity',
					'CNotificationActivity',
					'CExceptionHandler',
					'CTerminatorActivity',
					'CUserVarsActivity']
	search_types = ["JOB", "STAGE", "LINK", "STRING", "PARAMETER"]
	def __init__(self, properties):
		self.jobs = []
		self.properties = properties
		self.header = properties["header"]
		self.factory()
	def factory(self):
		self.jobs = map(lambda x: Job(x), self.properties["jobs"])
	def search(self, search_type="STAGE", where={"stagetype":"CTransformerStage"}):
		results = []
		if search_type in DSX.search_types:
			if search_type == "JOB":
				for job in self.jobs:
					for stage in job.stages:
						found = True
						for key, value in where.iteritems():
							if stage.properties[key] != value:
								found = False
						if found:
							#stage.job = job
							results.append(job)
			if search_type == "STAGE":
				for job in self.jobs:
					for stage in job.stages:
						found = True
						for key, value in where.iteritems():
							if stage.properties[key] != value:
								found = False
						if found:
							stage.job = job
							results.append(stage)
			elif search_type == "LINK":
				for job in self.jobs:
					for link in job.links:
						found = True
						for key, value in where.iteritems():
							if link.properties[key] != value:
								found = False
						if found:
							link.job = job
							results.append(link)
			elif search_type == "PARAMETER":
				for job in self.jobs:
					for sub in job.properties["subrecords"]:
						found = True
						for key, value in where.iteritems():
							if sub.get(key, None) != value:
								found = False
						if found:
							sub["job"] = job
							results.append(sub)
			elif search_type == "STRING":
				for job in self.jobs:
					print where
					m = re.search(where["regex"], job.properties["raw"])
					if m:
						print m
						results.append(job)
			return results		
		else:
			raise Exception("Search type invalid")
		
class Job(object):
	def __init__(self, properties):
		self.properties = properties
		self.records = properties["records"]
		self.stages = []
		self.links = []
		self.annotations = []
		self.job_definitions = []
		self.container_views = []
		self.factory()
		del self.properties["records"]
		del self.records
	def __str__(self):
		return self.properties["identifier"]
	def __repr__(self):
		return self.properties["identifier"]

	def factory(self):
		for record in self.records:
			obj = Record(record).factory()
			if issubclass(obj.__class__, Stage):
				self.stages.append(obj)
			elif issubclass(obj.__class__, Link):
				self.links.append(obj)
			elif issubclass(obj.__class__, Annotation):
				self.annotations.append(obj)
			elif issubclass(obj.__class__, ContainerView):
				self.container_views.append(obj)
			elif issubclass(obj.__class__, JobDefinition):
				z = obj.properties.copy()
				self.properties.update(z)
				self.properties["category"] = self.properties["category"].replace('\\\\', '/')


class OracleConnectorStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties) 
		self.properties = properties
class RemoveDuplicatesStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties) 
		self.properties = properties
class CopyStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties) 
		self.properties = properties
class TransformerStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties)
		self.properties = properties
class SequentialFileStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties)
		self.properties = properties
class ExceptionHandlerStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties)
		self.properties = properties
class JobActivityStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties)
		self.properties = properties
class NotificationActivityStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties)
		self.properties = properties
class MailActivityStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties)
		self.properties = properties
class TerminatorActivityStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties)
		self.properties = properties
class UserVarsActivityStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties)
		self.properties = properties
class AggregatorStage(Stage):
	def __init__(self, properties):
		super(Stage, self).__init__(properties)
		self.properties = properties

#class SubRecord(object):


class DSXParser(object):
	def __init__(self, filename=None, data=None):
		self.filename = filename
		self.data = data
	def parse(self):
		if self.filename:
			with open(self.filename) as f:
				dsx_dict = self.parse_dsx(f.read())
				d = DSX(dsx_dict)
				return d
		elif data:
			dsx_dict = self.parse_dsx(data)
			d = DSX(dsx_dict)
			return d
		else:
			print "No file or data specified"
			raise Exception
	def parse_dsx(self, dsx):
		dsx_dict = {"jobs":[]}
		lines = iter(dsx.split("\n"))
		while True:
			try:

				line = lines.next()
				if re.match(r'.*BEGIN HEADER.*', line):
					subr = line +"\n"
					while True:
						line = lines.next()
						subr += line + "\n"	
						if re.match(r'.*END HEADER.*', line):
							dsx_dict["header"] = self.parse_header(subr)
							break
				if re.match(r'.*BEGIN DSJOB.*', line):
					subr = line +"\n"
					while True:
						line = lines.next()
						subr += line + "\n"	
						if re.match(r'.*END DSJOB.*', line):
							dsx_dict["jobs"].append(self.parse_job(subr))
							break

			except StopIteration:
				break
		return dsx_dict		
	def parse_job(self, job):
		j_dict = {"records":[], "raw":""}
		raw = ""
		lines = iter(job.split("\n"))
		while True:
			try:
				line = lines.next()
				if re.match(r'.*BEGIN DSJOB.*', line):
					continue
				if re.match(r'.*END DSJOB.*', line):
					continue
				if re.match(r'.*BEGIN DSRECORD.*', line):
					subr = line +"\n"
					while True:
						line = lines.next()
						raw += line +"\n"
						subr += line + "\n"	
						if re.match(r'.*END DSRECORD.*', line):
							j_dict["records"].append(self.parse_record(subr))
							break
				if re.match(r'.*END DSRECORD.*', line):
					continue
				m = re.match('\s*(\w+)\s+?(.+)', line)
				if m:
					key = m.group(1).strip('"').lower()
					value = m.group(2).strip('"')
					if value.startswith('=+=+=+='):
						linegroup = value
						while True:
							try:
								line = lines.next()
								raw += line + "\n"
								linegroup += line +"\n"
								if line.startswith('=+=+=+='):
									break
							except StopIteration:
								break
						value = linegroup
						#value = None
					j_dict[key] = value
				#else:
					#print repr(line)
			except StopIteration:
				break
		j_dict["raw"] = raw
		return j_dict
	def parse_record(self, record):
		r_dict = {"subrecords":[]}
		lines = iter(record.split("\n"))
		while True:
			try:
				line = lines.next()
				if re.match(r'.*BEGIN DSRECORD.*', line):
					continue
				if re.match(r'.*END DSRECORD.*', line):
					continue
				if re.match(r'.*BEGIN DSSUBRECORD.*', line):
					subr = line +"\n"
					while True:
						line = lines.next()
						subr += line + "\n"	
						if re.match(r'.*END DSSUBRECORD.*', line):
							r_dict["subrecords"].append(self.parse_subrecord(subr))
							break
				if re.match(r'.*END DSSUBRECORD.*', line):
					continue
				m = re.match('\s*(\w+)\s+?(.+)', line)
				if m:
					key = m.group(1).strip('"').lower()
					value = m.group(2).strip('"')
					if value.startswith('=+=+=+='):
						linegroup = value
						while True:
							try:
								line = lines.next()
								linegroup += line +"\n"
								if line.startswith('=+=+=+='):
									break
							except StopIteration:
								break
						value = linegroup
						#value = None
					r_dict[key] = value
				#else:
					#print repr(line)
			except StopIteration:
				break
		return r_dict
	def parse_header(self, header):
		subr_dict = {}
		lines = iter(header.split("\n"))
		while True:
			try:
				line = lines.next()
				m = re.match('\s*(\w+)\s+?(.+)', line)
				if m:
					key = m.group(1).strip('"').lower()
					value = m.group(2).strip('"')
					if value.startswith('=+=+=+='):
						linegroup = value
						while True:
							try:
								line = lines.next()
								linegroup += line +"\n"
								if line.startswith('=+=+=+='):
									break
							except StopIteration:
								break
						value = linegroup
						#value = None
					subr_dict[key] = value
				#else:
					#print repr(line)
			except StopIteration:
				break
		return subr_dict
	def parse_subrecord(self, subr):
		subr_dict = {}
		lines = iter(subr.split("\n"))
		while True:
			try:
				line = lines.next()
				if re.match(r'.*BEGIN DSSUBRECORD.*', line):
					continue
				if re.match(r'.*END DSSUBRECORD.*', line):
					continue
				m = re.match('\s*(\w+)\s+?(.+)', line)
				if m:
					key = m.group(1).strip('"').lower()
					value = m.group(2).strip('"')
					if value.startswith('=+=+=+='):
						linegroup = value
						while True:
							try:
								line = lines.next()
								linegroup += line +"\n"
								if line.startswith('=+=+=+='):
									break
							except StopIteration:
								break
						value = linegroup
						#value = None
					subr_dict[key] = value
				#else:
					#print repr(line)
			except StopIteration:
				break
		return subr_dict
# if __name__ == "__main__":
# 	import sys, os
# 	dp = DSXParser(filename=sys.argv[1])
# 	d = dp.parse()
# 	for job in d.jobs:
# 		print job.properties["name"], job.properties["category"], os.path.dirname(sys.argv[1])
# 		target_dir = os.path.join(os.path.dirname(sys.argv[1]), "ABAP", job.properties["category"][1:])
# 		print target_dir
# 		for link in job.links:
# 			code = None
# 			prog_id = None
# 			for sub in link.properties["subrecords"]:
# 				if sub["name"] == "ABAPCODE":
# 					code = sub["value"].replace("=+=+=+=", "")
# 				if sub["name"] == "SAPPROGID":
# 					prog_id = sub["value"]
# 				if code != None and prog_id != None:
# 						print prog_id, code[0:10]
# 						try:
# 							os.makedirs(target_dir)
# 						except Exception as e:
# 							print e
# 						with open("%s/%s-%s.txt" % (target_dir, job.properties["name"], prog_id), 'w') as f:
# 							f.write(code)
# 						break	
def find_by_id(stages, idx):
	for stage in stages:
		#print "#", stage.properties["identifier"].strip(), idx
		if stage.properties["identifier"].strip() == idx.strip():
			return stage
	return None
if __name__ == "__main__":
	import sys
	mode = sys.argv[1]
	dp = DSXParser(filename=sys.argv[2])
	d = dp.parse()
	if mode == "showtree":
		def print_node(head, level=0):
			if not head.get("children"):
				return
			for child in head["children"]:
				print('    ' * (level-1) + '+---' + child["name"])
				print_node(child, level+1)
		def build(head, ins_and_outs):
			if not head["outputs"]:
				return 
			head["children"] = []
			for output in head["outputs"]:
				for item in ins_and_outs:
					if item["input"] == output:
						head["children"].append(item)
						del ins_and_outs[ins_and_outs.index(item)]
						build(item, ins_and_outs)
		for job in d.jobs:
			print "______________________________________________________"
			print job.properties["name"]
			ins_and_outs = []

			for stage in job.stages:
				try:

					tup = {"name":stage.properties["name"]}
					if stage.properties.get("inputpins"):
						tup["input"] = find_by_id(job.links, stage.properties.get("inputpins")).properties["name"]
					else:
						tup["input"] = None
					if stage.properties.get("outputpins"):
						tup["outputs"] = [find_by_id(job.links, i).properties["name"] for i in stage.properties.get("outputpins").split("|")]
					else:
						tup["outputs"] = None
					ins_and_outs.append(tup)

				except KeyError:
					pp.pprint(stage.properties)
			head = None
			for item in ins_and_outs:
				if item["input"] == None:
					head = item
					del ins_and_outs[ins_and_outs.index(item)]
					
					break
			build(head, ins_and_outs)
			print_node(head)
	elif mode == "showderivations":
		def find_source_from_link(link_id, stages):
			for stage in stages:
				if link_id in stage.properties.get("outputpins"):
					return stage
			return None
		for job in d.jobs:
			print "______________________________________________________"
			print job.properties["name"]
			for link in job.links:
				if link.properties["oletype"] == "CTrxOutput":

					source = find_source_from_link(link.properties["identifier"], job.stages)
					print source
					stage_vars = []
					for sub in source.properties["subrecords"]:
						try:
							stage_var = {"name":sub["name"], "expression":sub["expression"], "source_column":sub["sourcecolumn"]}
							stage_vars.append(stage_var)
							#print stage_var
						except KeyError:
							pass

					print "________________________________"

					for sub in link.properties["subrecords"]:
						if sub.get("derivation"):
							for sv in stage_vars:
								if sv["name"] in sub.get("derivation"):
									print sub.get("sourcecolumn"), "|", sub.get("derivation").replace(sv["name"], "#"+sv["expression"]+"#"), "|", sub.get("name")
									break
							print sub.get("sourcecolumn"), "|", sub.get("derivation"), "|", sub.get("name")

