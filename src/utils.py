import json
import os
import random
import string

import curl_cffi
from openpyxl import Workbook
from aiogram.types import Message
from aiogram.types import FSInputFile


def generate_random_filename(extension: str) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + extension


def count_lines_with_progress(filename):
    count = 0
    with open(filename, "r") as f:
        for _ in f:
            count += 1
    return count

async def parse_api(data: dict, site: str):

    headers = {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    }

    cookies = {"BSSESSID": data.get("token", "")}

    async with curl_cffi.AsyncSession() as session:
        request_params = {
            "args": {
                "competitors": [],
                "best_links_filter": "showAll",
                "backlinksFilter": None,
                "compareDate": ["Ago", "Year"],
                "multiTarget": [
                    "Single",
                    {"protocol": "both", "mode": "subdomains", "target": f"{site}/"},
                ],
                "url": f"{site}/",
                "protocol": "both",
                "mode": "subdomains",
            }
        }

        # Преобразуем словарь в JSON строку
        params = {"input": json.dumps(request_params)}

        try:
            response = await session.get(
                "https://app.ahrefs.com/v4/seGetMetricsByCountry",
                params=params,
                headers=headers,
                cookies=cookies,
            )
            if response.status_code == 200:
                result = response.json()
                if "SeInvalidUrl" in result:
                    return
                elif "Ok" in result:
                    return [x["country"] for x in result[1]["metrics"]]
            elif response.status_code == 401:
                return "Unauthorized"
            else:
                print(f"Failed to process {site}. Status code: {response.status_code}")

        except Exception as e:
            print(f"Error processing {site}: {str(e)}")


async def geo_process(data: dict, message: Message):
    result_dict = {}
    m = await message.answer("Starting processing")
    c = 0
    file_path = "files/" + data["random_filename"]
    line_count = count_lines_with_progress(file_path)
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            c += 1
            await m.edit_text(f"Progress: {c}/{line_count}")
            result = await parse_api(data, line.strip())
            if result == "Unauthorized":
                os.remove(file_path)
                await message.answer("Unauthorized")
                return
            if not result:
                continue
            result_dict[line] = result
    await message.answer("Read file")
    try:
        os.remove(file_path)
    except Exception as e:
        await message.answer(f"Failed to remove file {e}")
    await message.answer("File processed and deleted")
    excel_name = f"files/{generate_random_filename('.xlsx')}"
    await generate_excel(excel_name, result_dict)

    excel_file = FSInputFile(excel_name)
    await message.answer_document(document=excel_file)
    try:
        os.remove(excel_name)
    except Exception as e:
        await message.answer(f"Failed to remove file {e}")


async def generate_excel(excel_name, data):

    wb = Workbook()
    ws = wb.active

    for key, value in data.items():
        ws.append([key] + value)

    wb.save(excel_name)


if __name__ == "__main__":
    import asyncio


    data = {"token":""}
    site = ""
    asyncio.run(parse_api(data, site))
