#!/usr/bin/env python3
from requests_html import AsyncHTMLSession
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from imgcat import imgcat
from pathlib import Path
from rich import print
import pandas as pd
import requests
import asyncio
import json
import time
import sys
import os

# -- for importing parent module
sys.path.append(str(Path('.').absolute().parent))

from secret import username, password


class MMF_API:
    """API for Making Music Fun
    URL: https://makingmusicfun.net
    """
    def __init__(self, username: str, password: str):
        self.base_url = "https://makingmusicfun.net"
        self.url_login = "https://makingmusicfun.net/login.php"
        self.session = AsyncHTMLSession()
        self.loop = asyncio.get_event_loop()
        self.r = self.login(username, password)
        self.sheet_music_pages = []
        self.sheet_music_files = []

    def login(self, username: str, password: str):
        return self.loop.run_until_complete(self._login(username, password))

    async def _login(self, username: str, password: str):
        print("logging in ...")
        r = await self.session.get(self.url_login)
        await r.html.arender(keep_page=True)

        cmds = f"""
            document.querySelector('input[id="login"]').value="{username}";
            document.querySelector('input[id="password"]').value="{password}";
            document.querySelector('input[id="remember"]').click();
            document.querySelector('button[class="sign-in-btn"]').click();
        """
        login_commands = [cmd.strip() for cmd in cmds.splitlines() if cmd.strip()]
        for cmd in login_commands:
            await r.html.page.evaluate(cmd)
            imgcat(await r.html.page.screenshot(fullPage=True))
            time.sleep(0.2)

        cookies = await r.html.page.cookies()
        cookie_loggedin = dict(*map(dict, (c for c in cookies if c.get("name") == "loggedin")))
        print(cookie_loggedin)

        return r

    def scrapeSheetMusicPages(self, exportCSV=False, exportJSON=False):
        return self.loop.run_until_complete(self._scrapeSheetMusicPages(exportCSV, exportJSON))

    async def _scrapeSheetMusicPages(self, exportCSV=False, exportJSON=False):
        self.sheet_music_pages = []
        next_page = "https://makingmusicfun.net/htm/printit_piano_sheet_music_index.php"
        while True:
            print(f'accessing page: "{next_page}"')

            # -- navigate to sheet music index page
            await self.r.html.page.goto(url=next_page)
            time.sleep(10)

            imgcat(await self.r.html.page.screenshot(fullPage=True))
            soup = BeautifulSoup(await self.r.html.page.content(), "html5lib")
            time.sleep(4)

            # -- all non-premium sheet music
            for div_sheet_music in soup.select('div[class="divTableRow nonepremium"]'):
                links = div_sheet_music.select("a")
                if len(links) == 3:
                    sheet_music = {
                        "title": links[0].text,
                        "url": urljoin(self.base_url, links[0].attrs.get("href")),
                        "category": links[1].text,
                        "level": links[2].text,
                    }
                elif len(links) == 2:
                    sheet_music = {
                        "title": links[0].text,
                        "url": urljoin(self.base_url, links[0].attrs.get("href")),
                        "category": "no_category",
                        "level": links[1].text,
                    }
                elif len(links) == 1:
                    sheet_music = {
                        "title": links[0].text,
                        "url": urljoin(self.base_url, links[0].attrs.get("href")),
                        "category": "no_category",
                        "level": "no_level",
                    }
                else:
                    print("[red]WTF: NO LINKS !!![/]")
                self.sheet_music_pages.append(sheet_music)
                print(f"processed item: {sheet_music}")

            # -- next sheet music index page
            old_page = str(next_page)
            for div_page in soup.select('div[class="pagination-music-list"]'):
                for page_link in div_page.select("a"):
                    if "next" in page_link.text.lower():
                        next_page = urljoin(self.base_url, page_link.attrs.get("href"))
            if old_page == next_page:
                break
        if exportCSV:
            df = pd.DataFrame(self.sheet_music_pages)
            df.to_csv("sheet_music_pages.csv", index=False)

        if exportJSON:
            with open("sheet_music_pages.json", "w") as f:
                json.dump(self.sheet_music_pages, f)

    def scrapeSheetMusicFiles(self, exportCSV=False, exportJSON=False, downloadPDF=False):
        return self.loop.run_until_complete(self._scrapeSheetMusicFiles(exportCSV, exportJSON, downloadPDF))

    async def _scrapeSheetMusicFiles(self, exportCSV=False, exportJSON=False, downloadPDF=False):
        if not self.sheet_music_pages:
            self.scrapeSheetMusicPages()

        for page in self.sheet_music_pages:
            print(page)

            if dict(*filter(lambda x: x["url"] == page["url"], self.sheet_music_files)):
                print(f'skipping: {page["title"]}')
            else:
                await self.r.html.page.goto(url=urljoin(self.base_url, page["url"]))
                time.sleep(15)

                soup = BeautifulSoup(await self.r.html.page.content(), "html5lib")
                box_links = soup.select_one('div[class="content-item-box"]').select("a")
                pdf = next((a.attrs.get("href") for a in box_links if "pdf" in a.attrs.get("href").lower()), None)
                if pdf:
                    level = page["level"].replace(" ", "_")
                    parent = Path(f"pdf_files/{level}")
                    pdf_url = urljoin(self.base_url, pdf)
                    pdf_file = Path(parent, Path(pdf).name).as_posix()

                    if downloadPDF:
                        rr = requests.get(url=pdf_url)
                        parent.mkdir(exist_ok=True, parents=True)
                        with open(pdf_file, "wb") as f:
                            f.write(rr.content)

                    page["pdf_file"] = pdf_file
                    page["pdf_url"] = pdf_url
                    self.sheet_music_files.append(page)

                    print(pdf_file)
                    time.sleep(10)

        if exportCSV:
            df = pd.DataFrame(self.sheet_music_files)
            df.to_csv("sheet_music_files.csv", index=False)

        if exportJSON:
            with open("sheet_music_files.json", "w") as f:
                json.dump(self.sheet_music_files, f)

    def loadSheetMusicPages(self, file_name: str):
        self.sheet_music_pages = self.loadData(file_name)

    def loadSheetMusicFiles(self, file_name: str):
        self.sheet_music_files = self.loadData(file_name)

    def loadData(self, file_name: str):
        if Path(file_name).suffix.lower() == '.json':
            with open(file_name) as f:
                return json.load(f)
        if Path(file_name).suffix.lower() == '.csv':
            return pd.read_csv(file_name, header=0).to_dict('records')

    def quit(self):
        return self.loop.run_until_complete(self._quit())

    async def _quit(self):
        # await self.r.page.close()
        await self.session.close()

if __name__ == '__main__':
    mmf = MMF_API(username, password)
    mmf.scrapeSheetMusicPages(exportCSV=True, exportJSON=True)
    # mmf.loadSheetMusicPages('sheet_music_pages.json')
    # mmf.loadSheetMusicFiles('sheet_music_files.json')
    mmf.scrapeSheetMusicFiles(exportCSV=True, exportJSON=True, downloadPDF=True)
    mmf.quit()
