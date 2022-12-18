from pdfdataextractor.extraction import Reader
import glob

def extract_text(path, output_file):
    file = Reader()
    pdf = file.read_file(path)
    with open(output_file, 'w+', encoding="utf-8") as f:
        f.write(pdf)
    
    #print(pdf)


if __name__ == '__main__':
    path = r'data/decolonising-peacebuilding_schirch.pdf'
    output_file = r'data/output/decolonising-peacebuilding_schirch.txt'
    #path = r'data/acs.jcim.6b00207.pdf'
    extract_text(path, output_file)
    #print(pdf.abstract(chem=True).records.serialize())