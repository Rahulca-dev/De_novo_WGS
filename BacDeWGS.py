import gzip, sys, os, fileinput, argparse, subprocess, glob, re, shutil




def validation(R1_file, R2_file,name):
	
	print("-"*95 + "Fastq Validation" + "-"*95)
	os.system(' TrimGalore-0.6.6/trim_galore -q 30 --length 20 --paired  ' + R1_file + '  ' + R2_file +  " -o " + name)
	path = os.getcwd()
	npath = path + "/" + name
	source_dir = npath
	target_dir = path
	file_names = os.listdir(source_dir)
	for file_name in file_names:
		shutil.move(os.path.join(source_dir, file_name), target_dir)
	
	pass
def Assembly(TR1,TR2):
	print("-"*95 + "Genome Assembly" + "-"*95)
	os.system(" velveth Assembly 21 -short -separate -fastq " + TR1 + "  " + TR2)
	os.system(" velvetg Assembly")
	path = os.getcwd()
	npath = path + "/Assembly"
	source_dir = npath
	target_dir = path
	file_names = os.listdir(source_dir)
	for file_name in file_names:
		shutil.move(os.path.join(source_dir, file_name), target_dir)
	pass

def Alignment(TR1,TR2,ref_genome,name):
	print("-"*95 + "Genome Alignment" + "-"*95)
	os.system(" bwa index " + ref_genome)
	os.system("bwa mem  " + ref_genome +" "+ TR1 +" "+ TR2 + ">  " + name + ".sam")
	os.system("samtools view -S -b " + name + ".sam > "+ name +".bam")
	os.system("samtools sort -o "+ name +"_sorted.bam  " + name +".bam")
	pass

def Variant_calling(name,ref_genome):
	print("-"*95 + "Variant_calling" + "-"*95)

	os.system(" bcftools mpileup -O b -o " + name +".bcf -f " + ref_genome + " " + name + "_sorted.bam")
	os.system(" bcftools call --ploidy 1 -m -v -o " + name +".vcf " + name + ".bcf")

	pass
	
def Consesus(name,ref_genome):
	print("-"*95 + "Consesus genome Building" + "-"*95)
	os.system("bcftools view -O z -o "+ name +".vcf.gz  "+ name +".vcf")
	os.system("tabix -f -p vcf " + name +".vcf.gz")
	os.system("cat " + ref_genome +" | bcftools consensus "+name+".vcf.gz > " + name + ".fa")
	pass
def File_gen(name):
	f = open(name+".txt", 'w')
	f.writelines(name + "\n" + "Read Summary " + "\n")
	f.close()
	os.system("samtools flagstat " + name +".sam > " + name +".txt")
	with open(name+".txt") as fp:
		data = fp.read()
	with open(name+".vcf") as fp:
		data2 = fp.read()
	data += "\n"
	data += data2
	with open (name+".csv", 'w') as fp:
		fp.write(data)
	
	pass

path = os.getcwd();
parser = argparse.ArgumentParser(description='Test Code for variant analysis.')
parser.add_argument('-f1','--fastq1', help='Input file name',required=True)
parser.add_argument('-f2','--fastq2', help='Input file name',required=True)



args = parser.parse_args()
R1_file = args.fastq1
R2_file = args.fastq2
f = R1_file.split("_")
name = f[0]


validation(R1_file, R2_file,name)
read1 = glob.glob('*_val_1.fq')
read2 = glob.glob('*_val_2.fq')
TR1 = read1[0]
TR2 = read2[0]
Assembly(TR1,TR2)
fasta = glob.glob('*.fa')
ref_genome = fasta[0]
Alignment(TR1,TR2,ref_genome,name)
Variant_calling(name,ref_genome)
Consesus(name,ref_genome)
File_gen(name)
