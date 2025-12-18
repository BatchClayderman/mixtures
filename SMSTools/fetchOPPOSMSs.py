import os
from datetime import datetime
from re import findall
from bs4 import BeautifulSoup
os.chdir(os.path.abspath(os.path.dirname(__file__)))
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)


class Fetcher:
	def __init__(self:object, folderPath:str, initialMessageID:int = 1, initialThreadID:int = 1, offset:int = 10000) -> object:
		self.__folderPath = folderPath
		self.__messageID = initialMessageID if isinstance(initialMessageID, int) and initialMessageID >= 1 else 1
		self.__threadID = initialThreadID if isinstance(initialThreadID, int) and initialThreadID >= 1 else 1
		self.__offset = offset if isinstance(offset, int) and 1 <= offset <= 30000 else 10000 # set to 1 if too many messages are sent and received in a minute (maximum 60000)
	def __parseHtml(self:object, content:str) -> list:
		messages = []
		soup = BeautifulSoup(content, "html.parser")
		divs = soup.find_all("div")
		for div in divs:
			if not div.has_attr("style") or "display: none" not in div["style"]:
				for console in div.children:
					if "div" == console.name and console.has_attr("class") and "right_area" in console["class"]:
						address, lastTimestamp, timestamps, bodies, types = None, None, [], [], []
						for element in console.descendants:
							if "div" == element.name and element.has_attr("class"):
								if "item" in element["class"]:
									for subElement in element.descendants:
										if (													\
											"div" == subElement.name and subElement.has_attr("class") and "item_bg" in subElement["class"]	\
											and not (											\
												timestamps and timestamps[-1] // 60000 == lastTimestamp // 60000			\
												and bodies and bodies[-1] == subElement.contents[0]					\
											) # filter repeated backups									\
										):
											timestamps.append(lastTimestamp)
											lastTimestamp += self.__offset
											bodies.append(subElement.contents[0])
											types.append("2" if "mysms" in element["class"] else "1")
							elif "li" == element.name and element.has_attr("class"):
								if "date_key" in element["class"]:
									dt = tuple(int(integer) for integer in findall("\\d+", str(element.contents[0])))
									ts = int(datetime(*dt).timestamp()) * 1000
									if isinstance(lastTimestamp, int) and lastTimestamp // 60000 == ts // 60000:
										lastTimestamp += self.__offset # to avoid wrong orders
									else:
										lastTimestamp = ts
							elif "p" == element.name and element.has_attr("class"):
								if "address" in element["class"]: # address
									address = element.contents[0].replace("TEL:", "").replace(" ", "").replace("-", "")
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
			print("No valid OPPO HTML files were found. ")
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