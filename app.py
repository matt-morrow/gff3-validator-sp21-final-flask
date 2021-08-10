import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import re
import jinja2
#http://www.obofoundry.org/
#https://pypi.org/project/obonet/
#Used to create a dictionary of allowable SO terms (sequence_feature or child of) in column 3: type
import networkx
import obonet


UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'
DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
ALLOWED_EXTENSIONS = {'gff3', 'gff'}

app = Flask(__name__, static_url_path="/static")
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 8mb
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!DOCTYPE html>

    <head>
        <meta charset="utf-8">
        <title>GFF3 Validator</title>
        <style type="text/css">
            * {
                box-sizing: border-box;
                box-shadow: #333;
            }

            h1 {
                margin-bottom: 5px;
                font-size: 1em;
                text-align: center;
                font-weight: 700;
                color: rgb(88, 88, 88);
                padding: 5px 0 0 0;
            }

            .container-width {
                width: 100%;
                margin: 0 auto;
            }

            .flex-sect {
                background-color: #f3f3f3;
                padding: 5px 20px;
                font-family: Helvetica, serif;
            }

            .flex-title {
                margin-bottom: 25px;
                font-size: 2em;
                text-align: center;
                font-weight: 700;
                color: rgb(255, 255, 255);
                padding: 0 5px 0 0;
            }

            .cards {
                padding: 20px 0;
                display: flex;
                justify-content: space-around;
                flex-flow: wrap;
            }

            .form {
                border-radius: 3px;
                padding: 10px 15px;
                background-color: rgba(0, 0, 0, 0.2);
                left: auto;
                justify-content: flex-start;
                flex-direction: row;
                align-items: center;
            }

            .input {
                width: 100%;
                margin-bottom: 15px;
                padding: 7px 10px;
                border-radius: 2px;
                color: #fff;
                background-color: #554c57;
                border: none;
            }

            .label {
                width: 100%;
                display: block;
            }

            .button {
                width: 100%;
                margin: 15px 0;
                background-color: #785580;
                border: none;
                color: #fff;
                border-radius: 2px;
                padding: 7px 10px;
                font-size: 1em;
                cursor: pointer;
            }

            #card_css {
                display: flex;
                position: static;
                right: auto;
            }

            #search_term_form {
                background-image: linear-gradient(#d7d7d7, #d7d7d7);
                background-repeat: repeat;
                background-position: left top;
                background-attachment: scroll;
                background-size: auto;
            }

            #search_term_submit {
                background-image: linear-gradient(#e86464, #e86464);
                background-repeat: repeat;
                background-position: left top;
                background-attachment: scroll;
                background-size: auto;
            }

            #search_term_submit:hover {
                background-image: linear-gradient(#f15555, #f15555);
                background-repeat: repeat;
                background-position: left top;
                background-attachment: scroll;
                background-size: auto;
            }

            #search_term_submit:active {
                background-image: linear-gradient(#38c439, #38c439);
                background-repeat: repeat;
                background-position: left top;
                background-attachment: scroll;
                background-size: auto;
            }

            #search_term_label:active {
                padding: 2px 0 2px 0;
            }

            .navbar-items-c {
                display: inline-block;
                float: left;
            }

            .navbar {
                background-color: rgb(0, 0, 0);
                color: #ddd;
                min-height: 50px;
                width: 100%;
            }

            .navbar-container {
                margin: 0 auto;
                width: 95%;
            }

            .navbar-container::after {
                content: "";
                clear: both;
                display: block;
            }

            .navbar-menu {
                padding: 10px 0;
                display: block;
                float: right;
                margin: 0;
            }

            .navbar-menu-link {
                margin: 0;
                color: inherit;
                text-decoration: none;
                display: inline-block;
                padding: 10px 5px;
            }

            table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }

            td,
            th {
                border: 1px solid #4c4c4c;
                text-align: left;
                padding: 8px;
            }

            tr:nth-child(even) {
                background-color: #d2d2d2;
            }
        </style>
    </head>

    <body>
        <div data-gjs="navbar" class="navbar">
            <div class="navbar-container">
                <div class="navbar-burger">
                    <div class="navbar-burger-line">
                    </div>
                    <div class="navbar-burger-line">
                    </div>
                    <div class="navbar-burger-line">
                    </div>
                </div>
                <div data-gjs="navbar-items" class="navbar-items-c">
                    <nav data-gjs="navbar-menu" class="navbar-menu">
                        <a href="/" class="navbar-menu-link">Validator Home</a>
                    </nav>
                </div>
            </div>
        </div>
        <section class="flex-sect">
            <div class="container-width">
                <div class="flex-title">
                    <h1>Upload New File to Validate</h1>
                </div>
                <div class="cards" id="card_css">
                    <form method=post enctype=multipart/form-data>
                        <div class="form-group">
                            <label class="label" id="search_term_label" style="padding: 10px;">File</label>
                            <input type=file name=file>
                        </div>
                        <div class="form-group">
                            <input type=submit value=Upload class="button" id="search_term_submit">
                        </div>
                    </form>
                </div>
            </div>
        </section>
    </body>

    </html>
        
    '''

def process_file(path, filename):
    validateFile(path, filename)
    # with open(path, 'a') as f:
    #    f.write("\nAdded processed content")

def validateFile(path, filename):
    #Source: http://www.obofoundry.org/ontology/so.html
    #http://purl.obolibrary.org/obo/so.owl
    soFile = 'http://purl.obolibrary.org/obo/so.obo'
    soGraph = obonet.read_obo(soFile)

    #method to look up name by ID
    id_to_name_so = {id_: data.get('name') for id_, data in soGraph.nodes(data=True)}

    #create list of subterms (child of) for SO:0000110 (sequence_feature)
    subtermOfSeqFeature = [id_to_name_so[subterm] for subterm in networkx.ancestors(soGraph, 'SO:0000110')]
    subtermOfSeqFeature.append("sequence_feature")

    #create list of subterm IDs (child of) for SO:0000110 (sequence_feature)
    subtermOfSeqFeatureID = [subterm for subterm in networkx.ancestors(soGraph, 'SO:0000110')]
    subtermOfSeqFeatureID.append("SO:0000110")

    #Create a dictionary of TermID:Name features allowed
    termDictSO = dict(zip(subtermOfSeqFeatureID, subtermOfSeqFeature))

    #Source: http://www.obofoundry.org/ontology/go.html
    #Used to create a dictionary of allowable GO terms if used in column 9: attributes
    goFile = 'http://purl.obolibrary.org/obo/go.obo'
    goGraph = obonet.read_obo(goFile)
    id_to_name_go = {id_: data.get('name') for id_, data in goGraph.nodes(data=True)}

    #Used to lookup valid database references as of July 2021
    #https://www.ncbi.nlm.nih.gov/genbank/collab/db_xref/
    db_xrefs_lookup = ["AceView/WormGenes","AFTOL","AntWeb","APHIDBASE","ApiDB","ApiDB_CryptoDB","ApiDB_PlasmoDB","ApiDB_ToxoDB","Araport","ASAP","ATCC","ATCC(dna)","ATCC(in host)","Axeldb","BDGP_EST","BDGP_INS","BEEBASE","BEETLEBASE","BEI","BGD","BOLD","CABRI","CCAP","CDD","CGD","dbEST","dbProbe","dbSNP","dbSTS","dictyBase","ECOCYC","EcoGene","ENSEMBL","EnsemblGenomes","EnsemblGenomes-Gn","EnsemblGenomes-Tr","EPD","ERIC","ESTLIB","FANTOM_DB","FBOL","FLYBASE","Fungorum","GABI","GDB","GeneDB","GeneID","GI","GO","GOA","Greengenes","GRIN","HGNC","H-InvDB","HMP","HOMD","HPM","HSSP","I5KNAL","IKMC","IMGT/GENE-DB","IMGT/HLA","IMGT/LIGM","InterPro","IntrepidBio","IRD","ISFinder","ISHAM-ITS","JCM","JGI Phytozome","JGIDB","LocusID","MaizeGDB","MarpolBase","MedGen","MGI","MIM","miRBase","MycoBank","NBRC","NextDB","niaEST","NMPDR","NRESTdb","OrthoMCL","Osa1","Pathema","PBmice","PDB","PFAM","PGN","PIR","PomBase","PSEUDO","PseudoCAP","RAP-DB","RATMAP","RBGE_garden","RBGE_herbarium","RFAM","RGD","RiceGenes","RNAcentral","RZPD","SEED","SGD","SGN","SK-FST","SoyBase","SRPDB","SubtiList","TAIR","taxon","TIGRFAM","TubercuList","UNILIB","UniProtKB/Swiss-Prot","UniProtKB/TrEMBL","UniSTS","UNITE","VBASE2","VectorBase","VGNC","ViPR","VISTA","WorfDB","WormBase","Xenbase","ZFIN"]

    # TEST: Identify file encoding type
    """import chardet
    rawdata = open("./tab_delimiter_url.gff3", "rb").read()
    result = chardet.detect(rawdata)
    charenc = result['encoding']
    print(charenc)"""

    #Section Lists
    directiveSection = []
    summarySection = []
    commentSection = []
    errors = []
    idAttribute = {}
    fasta = ''
    Gap = ['M', 'I', 'D', 'F', 'R']
    tabDelimitedLine = True
    seqIDBound = ''
    seqStartBound = ''
    seqEndBound = ''

    def checkSeqID(columnOne):
        if (re.search('[^a-zA-Z0-9\.\:\^\*\$\@\!\+\_\?\-\|]', columnOne)):
            
            if(re.search(' ', columnOne)):
                return False
            elif columnOne.startswith(">"):
                return False
            else: 
                return True
        else:
            return True
    def checkType(columnThree):
        if(columnThree.startswith("SO:")):
            if columnThree not in termDictSO:
                return False
            else: 
                return True
        
        else:
            if columnThree not in termDictSO.values():
                return False
            else:
                return True
    def checkStart(columnFour):
        if columnFour.isnumeric():
            return True
        else:
            return False
    def checkEnd(columnFive):
        if columnFive.isnumeric():
            return True
        else:
            return False
    def checkDifference(columnFour, columnFive):
        if (int(columnFour) <= int(columnFive)):
            return True
        else:
            return False
    def checkScore(columnSix):
        if(columnSix == "."):
            return True
            
        else:
            try:
                if(isinstance(float(columnSix), float)):
                    return True
            except:
                return False
            
            else:
                return False
    def checkStrand(columnSeven):
        if(columnSeven == "+" or columnSeven == "-" or columnSeven == "." or columnSeven == "?"): 
            return True
        else:
            return False
    def checkPhase(columnThree, columnEight):
        if(columnThree == "CDS" or columnThree == "SO:0000316"):
            if(columnEight == "0" or columnEight == "1" or columnEight == "2"):
                return True
            else:
                return False
        
        elif(columnEight == "."):
            return True
        
        else:
            return False
    def checkAttributes(columnNine, lineIndex, line):
        splitAttributes = re.split(';', columnNine)
        
        for attributes in splitAttributes:
            splitAttribute = re.split('=', attributes)
            
            #URL escaping rules are used for tags or values containing the following characters: ",=;".
            if(len(splitAttribute) != 2):
                errors.append(["Error","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + attributes + ") contains unescaped '=' characters.", "URL escaping rules are used for tags or values containing the equal sign.", lineIndex, line])
            
            #Check for duplicated ID's that are not sequentially used in the GFF3 file
            if(splitAttribute[0] == "ID"):
                if splitAttribute[1] in idAttribute.keys() and lineIndex - 1 != idAttribute[splitAttribute[1]]:
                    errors.append(["Error","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + attributes + ") is a non-allowed use of a repeated ID.", "Note: All lines that share an ID must collectively represent a single feature sequentially.", lineIndex, line])
                elif splitAttribute[1] in idAttribute.keys():
                    idAttribute.pop(splitAttribute[1])
                    idAttribute[splitAttribute[1]] = lineIndex
                else:
                    idAttribute[splitAttribute[1]] = lineIndex
                
            # if (splitAttribute[0] == "Name"):                
            # if (splitAttribute[0] == "Alias"):
            # if (splitAttribute[0] == "Parent"):
            # if (splitAttribute[0] == "Note"):

            if (splitAttribute[0] == "Target"):
                attributeTarget = re.split(" ", splitAttribute[1])

                if(attributeTarget[1].isnumeric() and attributeTarget[2].isnumeric()):
                    if (len(attributeTarget) == 3):
                        if(int(attributeTarget[1]) > int(attributeTarget[2])):
                            errors.append(["Error","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + attributes + ") has a target start greater than target end.", "", lineIndex, line])
                    elif(len(attributeTarget) == 4):
                        if not(attributeTarget[3] == "+" or attributeTarget[3] == "-"):
                            errors.append(["Error","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + attributes + ") has a non-allowed target strand.", "Strand is optional and may be '+' or '-'.", lineIndex, line])
                        if(int(attributeTarget[1]) > int(attributeTarget[2])):
                            errors.append(["Error","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + attributes + ") has a target start greater than target end.", "", lineIndex, line])
                else:
                    errors.append(["Warning","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + attributes + ") appears to have unescaped spaces in target_id.", "If the target_id contains spaces, they must be escaped as hex escape %20.", lineIndex, line])
                

            if (splitAttribute[0] == "Gap"):
                attributeGap = re.split(" ", splitAttribute[1])
                for gapItem in attributeGap:
                    if not gapItem.startswith(tuple(Gap)):
                        errors.append(["Error","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + attributes + ") has an unallowed Gap attribute code.",  "Allowed codes are M, I, D, F, or R.", lineIndex, line])

            #The examples given on the Sequence Ontology Github for GFF3 use unescaped quotes for Dbxref and Ontology_term so those are replaced. I believe they should be escaped. https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md#ontology-associations-and-db-cross-references
            if (splitAttribute[0] == "Dbxref"):
                attributeDB = splitAttribute[1].replace('\"', '')
                attributeDBRefList = re.split(",", attributeDB, maxsplit=1)
                for attr in attributeDBRefList:
                    attributeDBRef = re.split(":", attr, maxsplit=1)
                    if (attributeDBRef[0] not in db_xrefs_lookup):
                        errors.append(["Warning","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + attributeDBRef[0] + ") has an invalid Dbxref value." , "The list of Dbxref used for this validator can be found at <a href='https://www.ncbi.nlm.nih.gov/genbank/collab/db_xref/'>db_xref</a>.", lineIndex, line])

            if (splitAttribute[0] == "Ontology_term"):
                attributeOntology = splitAttribute[1].replace('\"', '')
                attributeOntologyList = re.split(",", attributeOntology, maxsplit=1)
                for onto in attributeOntologyList:
                    if(onto.startswith("GO:")):
                        if onto not in id_to_name_go:
                            errors.append(["Error","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + onto + ") is not a valid Ontology_term.", "Use the GO Browser here to verify the term used: <a href='http://geneontology.org/'>GeneOntology</a>", lineIndex, line])

                    else:
                        if onto not in id_to_name_go.values():
                            errors.append(["Error","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + onto + ") is not a valid Ontology_term.", "Use the GO Browser here to verify the term used: <a href='http://geneontology.org/'>GeneOntology</a>", lineIndex, line])

            if (splitAttribute[0] == "Is_circular"):
                if(splitAttribute[1] != "true" or splitAttribute[1] != "false"):
                    errors.append(["Error","'attribute " + str(splitAttributes.index(attributes)+1) + "' (" + attributes + ") has a non-boolean value for 'Is_circular'.", "Allowed values are 'true' or 'false' if used.", lineIndex, line])
    with open(path, "rb") as inputFile:
        # encodedFile = inputFile.encode("utf-8")
        lines = inputFile.readlines()

        for line in lines:
            try:
                decodedLine = line.decode("utf-8").strip()
            except:
                errors.append(["Warning","Line is not UTF-8 encoded.", "The file contents may include any character in the set supported by the operating environment, although for portability with other systems, use of UTF-8 is recommended.", lines.index(line), decodedLine])

            #GFF3 FASTA Directive (##FASTA)
            ##Rule: 
            if(decodedLine.startswith('##FASTA')):
                fasta = str(lines.index(line))
                errors.append(["Notice","All FASTA sequences included in the file must be included together at the end of the file and may not be interspersed with the features lines.", "Once a ##FASTA section is encountered no other content beyond valid FASTA sequence is allowed.", lines.index(line), "This validator does not check to confirm the FASTA content or if is after the features lines in the GFF3 file. Use caution."])
                break
            
            #GFF3 Directives/Pragmas/Metadata (##.*)
            ##Rule: Lines beginning with '##' are directives (sometimes called pragmas or meta-data) and provide meta-information about the document as a whole. 
            elif(decodedLine.startswith('##')):
                directiveSection.append([decodedLine, lines.index(line), decodedLine])
                ##sequence-region
                ##The sequence segment referred to by this file, in the format "seqid start end".
                if(decodedLine.startswith('##sequence-region')):
                    boundsList = re.split(" ", decodedLine, maxsplit=3)
                    print(boundsList)
                    seqIDBound = boundsList[1]
                    
                    if (boundsList[2].isnumeric()):
                        seqStartBound = boundsList[2]
                    else:
                        seqStartBound = 'error'
                        errors.append(["Error","'##sequence-region start bound' (" + boundsList[2] + ") is not a numeric value.", "Cannot perform bound checking on the start column", lines.index(line), decodedLine])

                    if (boundsList[3].isnumeric()):
                        seqEndBound = boundsList[3]
                    else:
                        seqEndBound = 'error'
                        errors.append(["Error","'##sequence-region end bound' (" + boundsList[3] + ") is not a numeric value.", "Cannot perform bound checking on the start column", lines.index(line), decodedLine])

            #GFF3 Single # for Human Readable Comments
            ##Rule: Blank lines should be ignored by parsers and lines beginning with a single '#' are used for human-readable comments and can be ignored by parsers. End-of-line comments (comments preceded by # at the end of and on the same line as a feature or directive line) are not allowed.
            elif(decodedLine.startswith('#')):
                commentSection.append([decodedLine, lines.index(line)])        
            
            #
            else:
                #Split the line into the respective columns using either tab or percent encoded tab with max limit of 8 should Column 9 have tab encoding in it
                    splitColumn = re.split('\t|%09', decodedLine)
                    
                    if(len(splitColumn) != 9):
                        errors.append(["Warning","Line is not tab-delimited for nine columns. Attempting to split columns on other non-tab whitespaces.", "If columns contained unescaped spaces outside of column 9 (Attributes), the conversion only captures the first 8 whitespaces only. Review the line.", lines.index(line), decodedLine])
                        splitColumn = re.split('\s+', decodedLine, maxsplit=8)
                        if(len(splitColumn) != 9):
                            errors.append(["Error","Line is not tab-delimited for nine columns after non-tab white space split", "", lines.index(line), decodedLine])
                            tabDelimitedLine = False
                        else:
                            summarySection.append([splitColumn, lines.index(line), decodedLine])
                            tabDelimitedLine = True

                    else:
                        summarySection.append([splitColumn, lines.index(line), decodedLine])
                        tabDelimitedLine = True

                    
                    #Check column one (seqid)
                    if not (checkSeqID(splitColumn[0])) and tabDelimitedLine:
                        errors.append(["Error","'seqid' (" + splitColumn[0] + ") contains invalid characters.", "IDs may not contain unescaped whitespace and must not begin with an unescaped '>'.", lines.index(line), decodedLine])
                    
                    elif not tabDelimitedLine:
                        try:
                            if not (checkSeqID(splitColumn[0])):
                                errors.append(["Error","'seqid' (" + splitColumn[0] + ") contains invalid characters.", "IDs may not contain unescaped whitespace and must not begin with an unescaped '>'.", lines.index(line), decodedLine])
                        except:
                            errors.append(["Error","Cannot validate column one (seqid) due to delimitation issue.", "", lines.index(line), decodedLine])


                    # TODO: check column two (source)

                    #Check column three (type)
                    if not (checkType(splitColumn[2])) and tabDelimitedLine:
                        errors.append(["Error","'type' (" + splitColumn[2] + ") is not valid.", "This is constrained to be either a term from the Sequence Ontology or an SO accession number.<br><br>To verify the SO term, please use a child_of 'sequence_feature' which can be found here: <a href='http://sequenceontology.org/browser/current_release/term/SO:0000110'>SequenceOntology</a>", lines.index(line), decodedLine])
                    
                    elif not tabDelimitedLine:
                        try:
                            if not (checkType(splitColumn[2])):
                                errors.append(["Error","'type' (" + splitColumn[2] + ") is not valid.", "This is constrained to be either a term from the Sequence Ontology or an SO accession number.<br><br>To verify the SO term, please use a child_of 'sequence_feature' which can be found here: <a href='http://sequenceontology.org/browser/current_release/term/SO:0000110'>SequenceOntology</a>", lines.index(line), decodedLine])
                        except:
                            errors.append(["Error","Cannot validate column 3 (type) due to delimitation issue.", "", lines.index(line), decodedLine])

                    #Check column four (start) and check if the lower bound is satisfied, when provided
                    if not (checkStart(splitColumn[3])) and tabDelimitedLine and seqStartBound != "error":
                        errors.append(["Error","'start' (" + splitColumn[3] + ") is not valid.", "The start coordinate must be a positive 1-based integer.", lines.index(line), decodedLine])
                    
                    elif not tabDelimitedLine and seqStartBound != "error":
                        try:
                            if not (checkStart(splitColumn[3])):
                                errors.append(["Error","'start' (" + splitColumn[3] + ") is not valid.", "The start coordinate must be a positive 1-based integer.", lines.index(line), decodedLine])
                        except:
                            errors.append(["Error","Cannot validate column 4 (start) due to delimitation issue.", "", lines.index(line), decodedLine])

                    if(len(seqStartBound) != 0 and seqStartBound != 'error' and checkStart(splitColumn[3])):
                        if int(seqStartBound) > int(splitColumn[3]):
                            errors.append(["Error","'start' (" + splitColumn[3] + ") is before start bound in ##sequence-region (" + seqStartBound + ").", "The start column value must be greater than or equal to the start bound value.", lines.index(line), decodedLine])

                    #Check column five (end) and check if the upper bound is satisfied, when provided
                    if not (checkEnd(splitColumn[4])) and tabDelimitedLine and seqEndBound != "error":
                        errors.append(["Error","'end' (" + splitColumn[4] + ") is not valid.", "The end coordinate must be a positive 1-based integer.", lines.index(line), decodedLine])
                    
                    elif not tabDelimitedLine and seqEndBound != "error":
                        try:
                            if not (checkEnd(splitColumn[4])):
                                errors.append(["Error","'end' (" + splitColumn[4] + ") is not valid.", "The end coordinate must be a positive 1-based integer.", lines.index(line), decodedLine])
                        except:
                            errors.append(["Error","Cannot validate column five (end) due to delimitation issue.", "",  lines.index(line), decodedLine])
                    
                    if(len(seqEndBound) != 0 and seqEndBound != 'error' and checkStart(splitColumn[4])):
                        if int(seqEndBound) < int(splitColumn[4]):
                            errors.append(["Error","'end' (" + splitColumn[4] + ") is after end bound in ##sequence-region (" + seqEndBound + ").","The end column value must be less than or equal to the end bound value.", lines.index(line), decodedLine])

                    #Compare columns four and five (start <= end)
                    if checkStart(splitColumn[3]) and checkEnd(splitColumn[4]) and tabDelimitedLine:
                        if not checkDifference(splitColumn[3], splitColumn[4]):
                            errors.append(["Error","'start' (" + splitColumn[3] + ") is after 'end' (" + splitColumn[4] + ").","The start column value must be less than or equal to the end column value.", lines.index(line), decodedLine])
                    
                    elif not checkEnd(splitColumn[3]) and checkEnd(splitColumn[4]) and tabDelimitedLine:
                        errors.append(["Warning","'start' (" + splitColumn[3] + ") is not valid.", "The comparison to end cannot be performed.",  lines.index(line), decodedLine])
                    
                    elif checkEnd(splitColumn[3]) and not checkEnd(splitColumn[4]) and tabDelimitedLine:
                        errors.append(["Warning","'end' (" + splitColumn[4] + ") is not valid.", "The comparison to end cannot be performed.",  lines.index(line), decodedLine])
                    
                    elif not checkEnd(splitColumn[3]) and not checkEnd(splitColumn[4]) and tabDelimitedLine:
                        errors.append(["Warning","'start' (" + splitColumn[3] + ") + end' (" + splitColumn[3] + "are not valid.", "The comparison of start to end cannot be performed.",  lines.index(line), decodedLine])

                    elif not tabDelimitedLine:
                        try: 
                            if checkStart(splitColumn[3]) and checkEnd(splitColumn[4]) and tabDelimitedLine:
                                if not checkDifference(splitColumn[3], splitColumn[4]):
                                    errors.append(["Error","'start' (" + splitColumn[3] + ") is after 'end' (" + splitColumn[4] + ").","The start column value must be less than or equal to the end column value.", lines.index(line), decodedLine])
                            
                            elif not checkEnd(splitColumn[3]) and checkEnd(splitColumn[4]) and tabDelimitedLine:
                                errors.append(["Warning","'start' (" + splitColumn[3] + ") is not valid.", "The comparison to end cannot be performed.",  lines.index(line), decodedLine])
                            
                            elif checkEnd(splitColumn[3]) and not checkEnd(splitColumn[4]) and tabDelimitedLine:
                                errors.append(["Warning", "'end' (" + splitColumn[4] + ") is not valid.", "The comparison to end cannot be performed.",  lines.index(line), decodedLine])
                            
                            elif not checkEnd(splitColumn[3]) and not checkEnd(splitColumn[4]) and tabDelimitedLine:
                                errors.append(["Warning", "'start' (" + splitColumn[3] + ") + end' (" + splitColumn[3] + "are not valid.", "The comparison of start to end cannot be performed.",  lines.index(line), decodedLine])
                        
                        except:
                            errors.append(["Error", "Cannot validate start is less than or equal to end due to delimitation issue.", "",  lines.index(line), decodedLine])
                    
                    #Check column six (score)
                    if not checkScore(splitColumn[5]) and tabDelimitedLine:
                        errors.append(["Error", "'score' (" + splitColumn[5] + ") is not valid.", "The score of the feature must be a floating point number.", lines.index(line), decodedLine])
                    
                    elif not tabDelimitedLine:
                        try: 
                            if not checkScore(splitColumn[5]):
                                errors.append(["Error", "'score' (" + splitColumn[5] + ") is not valid.", "The score of the feature must be a floating point number.", lines.index(line), decodedLine])
                        except:
                            errors.append(["Error", "Cannot validate column 6 (score) due to delimitation issue.", "", lines.index(line), decodedLine])

                    #Check column seven (strand)
                    if not checkStrand(splitColumn[6]) and tabDelimitedLine:
                        errors.append(["Error", "'strand' (" + splitColumn[6] + ") is not valid.", "The strand of the feature can be + for positive strand (relative to the landmark), - for minus strand, and . for features that are not stranded. ? can be used for features whose strandedness is relevant, but unknown.", lines.index(line), decodedLine])
                    
                    elif not tabDelimitedLine:
                        try: 
                            if not checkStrand(splitColumn[6]):
                                errors.append(["Error", "'strand' (" + splitColumn[6] + ") is not valid.", "The strand of the feature can be + for positive strand (relative to the landmark), - for minus strand, and . for features that are not stranded. ? can be used for features whose strandedness is relevant, but unknown.", lines.index(line), decodedLine])
                        except:
                            errors.append(["Error", "Cannot validate column 7 (strand) due to delimitation issue.", "",  lines.index(line), decodedLine])

                    #Check column eight (phase)
                    if not checkPhase(splitColumn[2], splitColumn[7]) and tabDelimitedLine:
                        if(splitColumn[2] == "SO:0000316" or splitColumn[2] == "CDS"):
                            errors.append(["Error", "'phase' (" + splitColumn[7] + ") is not valid.","The phase is one of the integers 0, 1, or 2 and is required for all CDS features.", lines.index(line), decodedLine])
                        else:
                            errors.append(["Error", "'phase' (" + splitColumn[7] + ") is not valid.", "This feature does not allow for a phase.", lines.index(line), decodedLine])

                    elif not tabDelimitedLine:
                        try: 
                            if not checkPhase(splitColumn[2], splitColumn[7]):
                                errors.append(["Error", "'phase' (" + splitColumn[7] + ") is not valid.","The phase is one of the integers 0, 1, or 2 and is required for all CDS features.", lines.index(line), decodedLine])
                        except:
                            errors.append(["Error", "Cannot validate column 8 (phase) due to delimitation issue.", "", lines.index(line), decodedLine])
                    
                    #Check column nine (attributes)
                    if tabDelimitedLine:
                        checkAttributes(splitColumn[8], lines.index(line), decodedLine)
                    elif not tabDelimitedLine:
                        try:
                            checkAttributes(splitColumn[8], lines.index(line), decodedLine)
                        except:
                            errors.append(["Error", "Cannot validate column 9 (attributes) due to delimitation issue.", "",  lines.index(line), decodedLine])
    
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    env = jinja2.Environment(loader=templateLoader)
    template = env.get_template('errors.html')
    outputErrors = open(app.config['DOWNLOAD_FOLDER'] + filename + ".html", 'w')
    outputErrors.write(template.render(placeholder="seqIDBound", number=len(errors), errorsToTemplate=errors))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename + ".html")


if __name__ == "__main__":
    app.run(host='0.0.0.0')
