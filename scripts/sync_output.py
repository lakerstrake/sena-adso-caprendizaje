import shutil
import os

shutil.copy("README.md", "output/README.md")
shutil.copy("LICENSE", "output/LICENSE")
shutil.copy("wrangler.toml", "output/wrangler.toml")
shutil.copy(".gitignore", "output/.gitignore")

print("Files synchronized to output/ successfully!")
