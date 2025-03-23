from punito.processing.preprocessor import get_chunked_code
from pathlib import Path
from punito.utils import read_file, write_to_file
from utils import save_chunks
import json



def main():
    class_path = Path(
        r"C:\moeve_IDE\moeve-ide\workspaces\main\moeve-vvst\moeve-enst-dlg\src\main"
        r"\java\de\itzbund\moeve\enst\taxation\taxation\dlg\af200\controller"
        r"\Af200EnergyBasicdataGeneralPanelControllerBean.java"
    )

    class_code = read_file(class_path)

    chunked_code = get_chunked_code(class_code)

    save_chunks(json.dumps(chunked_code), Path(__file__).parent / "debug" / "get_chunked_code" / "chunked_code.txt" )

if __name__ == "__main__":
    main()