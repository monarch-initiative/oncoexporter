# README downloaded_files
This directory is where we download certain files from the web. The code only downloads the files once, because we
assume that they are static within the time course of using this package. To override this, call the corresponing
"load" methods with overwrite=True.

We have added the file Neoplasm_Core.tsv to the repository. This file was downloaded on Jan 14, 2024, from
https://ncit.nci.nih.gov/ncitbrowser/ajax?action=values&vsd_uri=http://evs.nci.nih.gov/valueset/C126659#, representing
NCIt Neoplasm Core Terminology (http://evs.nci.nih.gov/valueset/C126659) and is useful for generating lists of synonyms.