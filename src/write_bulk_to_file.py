import csv, yaml

def write_bulk_to_file(fps, datas, format='csv'):

	for fp, data in zip(fps, datas):
		
		print(f'Writing to {fp}')

		with open(fp, 'w', encoding='utf-8', newline='') as f:
			
			if format == 'csv':
				spamwriter = csv.writer(f, delimiter='\t')
				if type(data) == dict:
					spamwriter.writerows(data.items())
				else:
					spamwriter.writerows(data)
			
			elif format == 'yaml':
				yaml.dump(data, f, allow_unicode=True)