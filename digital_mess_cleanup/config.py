APP_TITLE = "Digital Mess Cleanup"

SIMILARITY_THRESHOLD = 6

AI_MODEL_NAME = "openai/clip-vit-base-patch32"
AI_BALANCED_MODEL_NAME = "openai/clip-vit-base-patch16"
AI_ACCURATE_MODEL_NAME = "openai/clip-vit-large-patch14"
AI_MODEL_OPTIONS = {
    "Fast (recommended)": AI_MODEL_NAME,
    "Balanced": AI_BALANCED_MODEL_NAME,
    "Higher accuracy (slower)": AI_ACCURATE_MODEL_NAME,
}

AI_PROMPT_TEMPLATES = (
    "{}",
    "a photo of {}",
    "an image showing {}",
)



FILE_CATEGORIES = {

    "Images": {

        ".jpg", ".jpeg", ".png", ".gif", ".bmp",

        ".webp", ".tiff", ".tif", ".ico", ".heic",

        ".heif", ".avif",

    },

    "Documents": {

        ".pdf", ".doc", ".docx", ".txt", ".rtf",

        ".odt", ".md", ".pages",

    },

    "Spreadsheets": {

        ".xls", ".xlsx", ".csv", ".ods", ".tsv",

    },

    "Presentations": {

        ".ppt", ".pptx", ".odp", ".key",

    },

    "Videos": {

        ".mp4", ".mkv", ".mov", ".avi", ".wmv",

        ".flv", ".webm", ".m4v", ".mpeg", ".mpg",

    },

    "Audio": {

        ".mp3", ".wav", ".aac", ".flac", ".ogg",

        ".m4a", ".wma", ".opus",

    },

    "Archives": {

        ".zip", ".rar", ".7z", ".tar", ".gz",

        ".bz2", ".xz",

    },

    "Code": {

        ".py", ".java", ".c", ".cpp", ".h", ".cs",

        ".js", ".ts", ".html", ".css", ".php",

        ".json", ".xml", ".yaml", ".yml", ".sql",

        ".ipynb", ".sh", ".bat", ".ps1",

    },

}



IMAGE_EXTENSIONS = FILE_CATEGORIES["Images"]



AI_LABELS = [

    "a screenshot of a computer or mobile phone screen",

    "a photograph or scan of handwritten notes or a document",

    "a photograph of a receipt, bill, or invoice",

    "a photograph of nature, mountains, plants, or scenery",

    "a photograph of an animal or pet",

    "a photograph of food or drinks",

    "a photograph of people or a family",

    "a meme or internet graphic containing text",

    "a drawing, painting, illustration, or digital artwork",

    "a photograph of a product or object",

    "a photograph of a building or interior",

    "a chart, diagram, infographic, or presentation slide",

    "a photograph of a vehicle",

    "a photograph of a landscape or travel destination",

    "an image that does not fit the other categories",

]



AI_FOLDER_NAMES = {

    AI_LABELS[0]: "Screenshots",

    AI_LABELS[1]: "Notes_and_Documents",

    AI_LABELS[2]: "Receipts_and_Invoices",

    AI_LABELS[3]: "Nature_and_Scenery",

    AI_LABELS[4]: "Animals_and_Pets",

    AI_LABELS[5]: "Food_and_Drinks",

    AI_LABELS[6]: "People_and_Family",

    AI_LABELS[7]: "Memes_and_Graphics",

    AI_LABELS[8]: "Artwork_and_Illustrations",

    AI_LABELS[9]: "Product_Photos",

    AI_LABELS[10]: "Buildings_and_Interiors",

    AI_LABELS[11]: "Charts_and_Diagrams",

    AI_LABELS[12]: "Vehicles",

    AI_LABELS[13]: "Travel_Photos",

    AI_LABELS[14]: "Other_Images",

}





# --------------------------------------------------

# CUSTOM CSS — GREEN, BLACK & WHITE THEME

# --------------------------------------------------
