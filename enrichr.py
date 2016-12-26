#! /usr/bin/python
# Script to perform Enrichr enrichment analysis (http://amp.pharm.mssm.edu/Enrichr/)
# Based on code available on enrichr website, 
# adapted by wdecoster

import pandas, json, requests, sys, io, os



databases = ['Achilles_fitness_decrease', 'Achilles_fitness_increase', 'Aging_Perturbations_from_GEO_down', 'Aging_Perturbations_from_GEO_up', 
	'Allen_Brain_Atlas_down', 'Allen_Brain_Atlas_up', 'BioCarta_2013', 'BioCarta_2015', 'BioCarta_2016', 'Cancer_Cell_Line_Encyclopedia', 'ChEA_2013', 'ChEA_2015',
	'Chromosome_Location', 'CORUM', 'dbGaP', 'Disease_Perturbations_from_GEO_down', 'Disease_Perturbations_from_GEO_up', 'Disease_Signatures_from_GEO_down_2014', 'Disease_Signatures_from_GEO_up_2014',
	'Drug_Perturbations_from_GEO_2014', 'Drug_Perturbations_from_GEO_down', 'Drug_Perturbations_from_GEO_up', 'ENCODE_and_ChEA_Consensus_TFs_from_ChIP-X',
	'ENCODE_Histone_Modifications_2013', 'ENCODE_Histone_Modifications_2015', 'ENCODE_TF_ChIP-seq_2014', 'ENCODE_TF_ChIP-seq_2015', 'Epigenomics_Roadmap_HM_ChIP-seq',
	'ESCAPE', 'Genes_Associated_with_NIH_Grants', 'GeneSigDB', 'Genome_Browser_PWMs', 'GO_Biological_Process_2013', 'GO_Biological_Process_2015', 'GO_Cellular_Component_2013',
	'GO_Cellular_Component_2015', 'GO_Molecular_Function_2013', 'GO_Molecular_Function_2015', 'GTEx_Tissue_Sample_Gene_Expression_Profiles_down', 'GTEx_Tissue_Sample_Gene_Expression_Profiles_up',
	'HMDB_Metabolites', 'HomoloGene', 'Human_Gene_Atlas', 'Human_Phenotype_Ontology', 'HumanCyc_2015', 'Humancyc_2016', 'KEA_2013', 'KEA_2015', 'KEGG_2013', 'KEGG_2015', 'KEGG_2016',
	'Kinase_Perturbations_from_GEO_down', 'Kinase_Perturbations_from_GEO_up', 'Ligand_Perturbations_from_GEO_down', 'Ligand_Perturbations_from_GEO_up', 'LINCS_L1000_Chem_Pert_down',
	'LINCS_L1000_Chem_Pert_up', 'LINCS_L1000_Kinase_Perturbations_down', 'LINCS_L1000_Kinase_Perturbations_up', 'LINCS_L1000_Ligand_Perturbations_down', 'LINCS_L1000_Ligand_Perturbations_up',
	'MCF7_Perturbations_from_GEO_down', 'MCF7_Perturbations_from_GEO_up', 'MGI_Mammalian_Phenotype_2013', 'MGI_Mammalian_Phenotype_Level_3', 'MGI_Mammalian_Phenotype_Level_4',
	'Microbe_Perturbations_from_GEO_down', 'Microbe_Perturbations_from_GEO_up', 'Mouse_Gene_Atlas', 'MSigDB_Computational', 'MSigDB_Oncogenic_Signatures', 'NCI-60_Cancer_Cell_Lines',
	'NCI-Nature_2015', 'NCI-Nature_2016', 'NURSA_Human_Endogenous_Complexome', 'Old_CMAP_down', 'Old_CMAP_up', 'OMIM_Disease', 'OMIM_Expanded', 'Panther_2015', 'Panther_2016', 'Pfam_InterPro_Domains',
	'Phosphatase_Substrates_from_DEPOD', 'PPI_Hub_Proteins', 'Reactome_2013', 'Reactome_2015', 'Reactome_2016', 'SILAC_Phosphoproteomics', 'Single_Gene_Perturbations_from_GEO_down',
	'Single_Gene_Perturbations_from_GEO_up', 'TargetScan_microRNA', 'TF-LOF_Expression_from_GEO', 'Tissue_Protein_Expression_from_Human_Proteome_Map', 'Tissue_Protein_Expression_from_ProteomicsDB',
	'Transcription_Factor_PPIs', 'TRANSFAC_and_JASPAR_PWMs', 'Virus_Perturbations_from_GEO_down', 'Virus_Perturbations_from_GEO_up', 'VirusMINT', 'WikiPathways_2013', 'WikiPathways_2015', 'WikiPathways_2016']

def senddata(genes):
	input = {
		'list': (None, '\n'.join(genes)),
		'description': (None, 'enrichR.py query')
		}
	response = requests.post('http://amp.pharm.mssm.edu/Enrichr/addList', files=input)
	if not response.ok:
		raise Exception('Error uploading gene list')
	queryId = json.loads(response.text)['userListId']	
	askgenelist(queryId, genes)
	return(queryId)
	
def askgenelist(id, inlist):	
	response = requests.get('http://amp.pharm.mssm.edu/Enrichr/view?userListId=%s' % id)
	if not response.ok:
		raise Exception('Error getting gene list back')
	returnedN = 0
	returnedL = json.loads(response.text)["genes"]
	for gene in inlist:
		if gene in returnedL:
			returnedN += 1
	print('{} genes succesfully recognized by enrichR'.format(returnedN))

def whichdb():
	standarddb = ['KEGG_2016', 'BioCarta_2016', 'WikiPathways_2016', 'Reactome_2016', 'GO_Biological_Process_2015', 'GO_Cellular_Component_2015', 'GO_Molecular_Function_2015', 'MSigDB_Computational', 'Panther_2016']	
	if len(sys.argv) >= 3:
		chosendb = [db for db in sys.argv[2:] if db in databases]
		if chosendb:
			return chosendb
		else:
			print("Could not find a valid database in arguments, falling back on default databases.")
			return standarddb
	else:
		print("Using {} default databases.".format(len(standarddb)))
		return standarddb

def procesinput():
	if sys.argv[1] == 'databases':
		for option in databases:
			print option
	elif sys.argv[1] == '-':
		genes = set([item.strip() for item in sys.stdin.readlines() if not item == ""])
	elif os.path.isfile(sys.argv[1]):
		with open(sys.argv[1]) as inputgenes:
			genes = set([item.strip() for item in inputgenes.readlines() if not item == ""])
	else:
		sys.exit("Invalid input.\nFirst argument should be path to file containing list of genes or '-' for when reading from stdin.\nUse 'databases' as first argument to get list of possible databases.")
	print('Input contains {} unique gene names'.format(len(genes)))	
	return genes

# def getresults(id, gene_set_library):
# 	filename = gene_set_library + '_enrichment'
# 	url = 'http://amp.pharm.mssm.edu/Enrichr/export?userListId=%s&filename=%s&backgroundType=%s' % (id, filename, gene_set_library)
# 	response = requests.get(url, stream=True)
# 	with open(filename + '.txt', 'wb') as output:
# 		for chunk in response.iter_content(chunk_size=1024): 
# 			if chunk:
# 				output.write(chunk)

def getresults(id, gene_set_library):
	filename = gene_set_library + '_enrichment'
	url = 'http://amp.pharm.mssm.edu/Enrichr/export?userListId=%s&filename=%s&backgroundType=%s' % (id, filename, gene_set_library)
	response = requests.get(url, stream=True)
	return response.text



genelist = procesinput()				
id = senddata(genelist)
if os.path.isfile(sys.argv[1]):
	fn = sys.argv[1] + ".xlsx"
else:
	fn = 'output.xlsx'

writer = pandas.ExcelWriter(fn)
for db in whichdb():	
	res = getresults(id, db)
	df = pandas.read_table(io.StringIO(res))
	df.to_excel(writer, sheet_name=db, index=False)
	writer.save()





