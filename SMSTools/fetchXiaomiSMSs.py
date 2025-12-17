import os
from datetime import datetime
from re import findall
from bs4 import BeautifulSoup
os.chdir(os.path.abspath(os.path.dirname(__file__)))
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)


class Fetcher:
	def __init__(self:object, folderPath:str, initialMessageID:int = 1, initialThreadID:int = 1) -> object:
		self.__folderPath = folderPath
		self.__messageID = initialMessageID if isinstance(initialMessageID, int) and initialMessageID >= 1 else 1
		self.__threadID = initialThreadID if isinstance(initialThreadID, int) and initialThreadID >= 1 else 1
	def __parseHtml(self:object, content:str) -> list:
		messages = []
		soup = BeautifulSoup(content, "html.parser")
		consoles = soup.find_all("div", class_ = "container-2Q5xm")
		for console in consoles:
			address, timestamps, bodies, types = None, [], [], []
			for element in console.descendants:
				if "div" == element.name and element.has_attr("class"):
					if "contact-1yu6a" in element["class"]: # address
						if address is None:
							address = element.contents[0].replace(" ", "").replace("-", "")
					elif "phoneNumber-bRnPq" in element["class"]: # number (priority)
						address = element.contents[0].replace(" ", "").replace("-", "")
					elif "date-cYYud" in element["class"]:
						dt = tuple(int(integer) for integer in findall("\\d+", element.contents[0]))
						ts = int(datetime(*dt).timestamp())
						if timestamps and timestamps[-1] // 1000 == ts: # to avoid wrong orders
							ts = ts * 1000 + timestamps[-1] % 1000 + 1
						else:
							ts *= 1000
						timestamps.append(ts)
						types.append("2" if "send-date-RQHgG" in element["class"] else "1")
					elif "receive-SLIkS" in element["class"] and "messageDetail-1_W9O" in element["class"]: # rMsg
						bodies.append(element.contents[0])
					elif "send-3QTdp" in element["class"] and "messageDetail-1_W9O" in element["class"]: # sMsg
						bodies.append(element.contents[0])
			for idx in range(len(bodies)):
				messages.append(												\
					{													\
						"_id":str(self.__messageID), "thread_id":str(self.__threadID), "address":str(address), 		\
						"date":str(timestamps[idx]), "date_sent":timestamps[idx], "protocol":"0", "read":"1", 		\
						"status":"-1", "type":str(types[idx]), "reply_path_present":"0", "body":bodies[idx], 		\
						"locked":"0", "sub_id":str(idx), "phone_id":"-1", "error_code":"-1", 				\
						"creator":"com.google.android.apps.messaging", "seen":"1", "priority":"-1", 			\
						"style_code":"0", "combine_id":"0", "deleted":"0", "m_id":"-1"					\
					}													\
				)
				self.__messageID += 1
			self.__threadID += 1
		return messages
	def proceed(self:object, encoding:str = "utf-8") -> tuple:
		successCnt, totalCnt, lines = 0, 0, []
		try:
			for root, dirs, files in os.walk(self.__folderPath):
				for f in files:
					if os.path.splitext(f)[1].lower() == ".html":
						filePath = os.path.join(root, f)
						totalCnt += 1
						try:
							with open(filePath, "r", encoding = encoding) as fp:
								content = fp.read()
							lines.extend(self.__parseHtml(content))
							successCnt += 1
						except BaseException as e:
							print("\"{0}\" -> {1}".format(filePath, e))
			return (successCnt, totalCnt, lines)
		except BaseException as e:
			return (successCnt, totalCnt, e)



def main() -> int:
	folderPath, outputFilePath = ".", "./messages.txt"
	fetcher = Fetcher(folderPath)
	successCnt, totalCnt, lines = fetcher.proceed()
	if isinstance(lines, list):
		if lines:
			try:
				with open(outputFilePath, "w", encoding = "utf-8") as f:
					f.write(str(lines))
					#for line in lines:
					#	f.write(str(line) + "\n")
				print("Successfully proceeded {0} / {1} HTML file(s). ".format(successCnt, totalCnt))
				errorLevel = EXIT_SUCCESS if successCnt == totalCnt else EXIT_FAILURE
			except BaseException as e:
				print("Failed to proceed due to the following exception. \n\t{0}".format(e))
				errorLevel = EOF
		else:
			print("No valid Xiaomi HTML files were found. ")
			errorLevel = EOF
	else:
		print("Unknown exceptions occurred. ")
		errorLevel = EOF
	try:
		print("Please press the enter key to exit ({0}). ".format(errorLevel))
		input()
	except:
		print()
	return errorLevel



if "__main__" == __name__:
	exit(main())