# Website Data Searcher EXE Builder

## 1) `site_searcher.py`

``` python
#!/usr/bin/env python3
...
# check ../webScraperExe/site_searcher.py
```

## 2) requirements.txt

    check ../webScraperExe/requirements.txt

## 3) Testing locally

    check ../webScraperExe/virtualEnv.bash

## 4) Build exe with PyInstaller

    check ../webScrapperExe/pyinstaller.bash

## 5) Usage examples

-   Extract links:

```{=html}
<!-- -->
```
    site_searcher.exe --url "https://news.ycombinator.com" --selector "a.storylink" --attr "href" --output hn_links.csv

-   Save titles as JSON:

```{=html}
<!-- -->
```
    site_searcher.exe --url "https://example.com/blog" --selector ".post-title" --text --output titles.json

## 6) Packaging tips

-   Use `--onefile` for single exe.
-   Use `--onedir` for smaller build.
-   Selenium + webdriver-manager requires Chrome.

## 7) Legal & Ethical Notes

-   Respect robots.txt and TOS.
-   Do not overload servers.
-   Prefer official APIs for production use.
