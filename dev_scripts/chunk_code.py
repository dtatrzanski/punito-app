from punito.processing.preprocessor import get_chunked_code
from pathlib import Path
from punito.utils import read_file
from dev_utils import save_chunks
import json



def main():
    """
    Script for chunking the code and saving the result in a readable format.
    """
    class_path = r"C:\moeve_IDE\moeve-ide\workspaces\master\moeve-vvst\moeve-enst-dlg\src\main\java\de\itzbund\moeve\enst\permission\application\dlg\af100\controller\OtherAdmissionsPanelControllerBean.java"
    class_code = read_file(Path(class_path))

    chunked_code = get_chunked_code(class_code)
    save_chunks(json.dumps(chunked_code), Path(__file__).parent / "debug" / "latest" / "chunked_code" / "chunked_code.txt" )

if __name__ == "__main__":
    main()