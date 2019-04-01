import os 
import datetime
import re
import sys
import urllib.request
import zipfile
global START_DATE, DURATION

#! Product: 	Simple parser for solar and Earth's magnetic sci data
#! Dev: 	@ngh7mr3
#! License:	MIT
#! Source: 	https://github.com/ngh7mr3/sci-data
#! 2019 

if len(sys.argv)<3:
	sys.exit("You should include start date in format DD/MM/YYYY and experiment duration!")

START_DATE = sys.argv[1]
if not re.match(r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d', START_DATE):
	sys.exit('Your start day is wrong!')

DURATION = int(sys.argv[2])
if DURATION<=0:
	sys.exit("Duration must be > 0!")

class Parser():

	def __init__(self, name, template_url, time_offset, start_line, hour_col, minute_col, collumns_to_save):
		self.name = name
		self.template_url = template_url
		self.time_offset = time_offset
		self.start_hour = time_offset%24
		self.dates_to_search = self.calc_dates()
		self.start_line = start_line
		self.hour_col = hour_col
		self.minute_col = minute_col
		self.collumns_to_save = collumns_to_save
		self.parsed_data = []
		self.files_saved = []

		#!
		print("\nStarted downloading file(s) for "+self.name)
		self.download()

		#!
		print("\nStarted parsing "+self.name+"\'s file(s)")
		self.parse()

		#!
		print("Clearing downloads...")
		self.clear_downloads()

	def calc_dates(self):
		start_date = datetime.datetime.strptime(START_DATE, '%d/%m/%Y')+datetime.timedelta(hours=self.time_offset)
		day_delta = datetime.timedelta(days=1)
		
		return [(start_date+day_delta*i).strftime("%d %m %Y").split() \
		 for i in range(DURATION if self.time_offset==0 else DURATION+1)]

	def download(self):
		file_format = self.template_url.split('.')[-1]

		for Day, Month, Year in self.dates_to_search:
			base_url = self.template_url

			for x, y in [["{D}", Day],["{M}", Month],["{Y}", Year]]:
				base_url = base_url.replace(x,y)

			file_name = base_url.split('/')[-1]
			file_path = os.getcwd()+"//"+file_name

			#! Trying to find txt rather than a zip
			if not os.path.isfile(file_name.replace('zip','txt')):
				try:
					print("Downloading "+file_name)

					urllib.request.urlretrieve(base_url, file_path)

					if file_format == 'zip':
						zip_file = zipfile.ZipFile(file_path, 'r')
						zip_file.extractall()
						zip_file.close()
						os.system('del '+file_name)
						file_name = file_name.replace('zip', 'txt')
					elif file_format != 'txt':
						sys.exit("Unsupported file has been downloaded! Improve the script or contact a dev.")

					self.files_saved.append(file_name)

				except Exception:
					print("Warning!\nNo such file or a directory provided by", base_url)
			else:
				print("File", file_name, "has been already downloaded!")
				self.files_saved.append(file_name.replace('zip', 'txt'))

	def parse(self):
		if len(self.files_saved)==0:
			print("Warning!\nThere are no saved files!")
			return

		for ind,file in enumerate(self.files_saved):
			if ind == 0:
				self.collect_file_data(file, start = self.start_hour)
			elif ind == len(self.files_saved)-1:
				self.collect_file_data(file, end = 24 if self.start_hour==0 else self.start_hour)
			else:
				self.collect_file_data(file)

	def collect_file_data(self, file, start = 0, end = 24, mode = 'hours'):

		print("Collecting data from "+file)

		data_file = open(file, 'r')
		data_lines = [i.split() for i in data_file.readlines()[self.start_line-1:]]
		data_file.close()

		next_hour = start+1

		for line in data_lines:
			cur_hour, cur_minute = self.get_time(line)

			#!
			# MSC_MAG missing data hourly
			# predict next hour
			if cur_hour>next_hour and cur_hour<end:
				
				for k in range(next_hour, cur_hour if cur_minute==0 else cur_hour+1):
					print("\nWARNING!")
					print("MISSING HOURLY DATA IN FILE "+file+" FOR HOUR "+str(k))
					print("THE DATA WILL BE NULLIFIED FOR THIS HOUR")
					self.parsed_data.append(['0' for i in range(len(self.collumns_to_save))])

				next_hour = cur_hour+1

			# Mode 'hours' means collecting data only in a start of the hour
			if cur_hour>=start and cur_hour<end and cur_minute==0:

				next_hour = cur_hour+1

				cur_data = [line[i-1] for i in self.collumns_to_save]
				
				# Deleting -9999 and -999 values from the ACE's data
				# Replacing with 0 
				if '-9999.9' in cur_data or '-999.9' in cur_data:
					cur_data = ['0']*len(cur_data)

				self.parsed_data.append(cur_data)

	def get_time(self, line):
		if self.hour_col != self.minute_col:
			return int(line[self.hour_col-1]), int(line[self.minute_col-1])
		else:
			# Parsing HHMM template
			return int(line[self.hour_col-1][:2]), int(line[self.hour_col-1][2:])
		
	def clear_downloads(self):
		for file in self.files_saved:
			os.system("del "+file)


if __name__ == "__main__":
	
	url_ace_swepam = 'ftp://ftp.swpc.noaa.gov/pub/lists/ace/{Y}{M}{D}_ace_swepam_1m.txt'
	ACE_swepam = Parser("ACE_swepam", url_ace_swepam,  -3, 19, 4, 4, [8,9])
	
	url_ace_mag = 'ftp://ftp.swpc.noaa.gov/pub/lists/ace/{Y}{M}{D}_ace_mag_1m.txt'
	ACE_mag = Parser("ACE_mag", url_ace_mag, -3, 21, 4, 4, [8,9,10]);
	
	url_msc_mag = 'http://forecast.izmiran.rssi.ru/BANK/mos/mos{Y}{M}/mos{Y}{M}{D}t.zip'
	MSC_mag = Parser("MSC_mag", url_msc_mag ,0, 7, 4, 5, [7,8,9])

	
	stored_data = [[str(i)] + ACE_swepam.parsed_data[i]+\
					ACE_mag.parsed_data[i]+\
					MSC_mag.parsed_data[i] for i in range(len(ACE_swepam.parsed_data))]

	csv = '_'.join(START_DATE.split('/'))+'_+'+str(DURATION)+'.csv'
	print("\nCollecting the data for "+START_DATE+" with duration "+str(DURATION)+" day(s) into "+csv)
	
	csv_file = open(csv, 'w')

	for i in stored_data:
		csv_file.write(','.join(i)+'\n')

	csv_file.close()
