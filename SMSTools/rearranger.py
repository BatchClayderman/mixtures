import os
from sys import exit
from re import finditer
os.chdir(os.path.abspath(os.path.dirname(__file__)))
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)


class Rearranger:
	def __init__(self:object, prefix:bytes = b"\"_id\":\"", suffix:bytes = b"\"") -> object:
		self.__prefix = prefix if isinstance(prefix, bytes) else b"\"_id\":\""
		self.__suffix = suffix if isinstance(suffix, bytes) else b"\""
		self.__items = []
	def readFile(self:object, filePath:str = "messages.ndjson") -> int|BaseException:
		try:
			with open(filePath, "rb") as f:
				content = f.read()
			self.__items.clear()
			idx, length, buffer, quotation, stack = 0, len(content), b"", False, []
			while idx < length:
				if 10 == content[idx]: # '\n'
					if not (quotation or stack):
						self.__items.append(buffer)
						buffer = b""
						idx += 1
						continue
				elif 34 == content[idx]: # '\"'
					quotation = not quotation
				elif content[idx] in (40, 91, 123): # ('(', '[', '{')
					if not quotation:
						stack.append(content[idx])
				elif 41 == content[idx]: # ')'
					if not quotation:
						if 40 == stack[-1]:
							stack.pop()
						else:
							raise ValueError("Failed to pop \'(\' when meeting \')\'. ")
				elif 92 == content[idx]: # '\\'
					buffer += content[idx:idx + 2]
					idx += 2
					continue
				elif 93 == content[idx]: # ']'
					if not quotation:
						if 91 == stack[-1]:
							stack.pop()
						else:
							raise ValueError("Failed to pop \'[\' when meeting \']\'. ")
				elif 125 == content[idx]: # '}'
					if not quotation:
						if 123 == stack[-1]:
							stack.pop()
						else:
							raise ValueError("Failed to pop \'{\' when meeting \'}\'. ")
				buffer += content[idx:idx + 1]
				idx += 1
			if buffer and buffer != b'\n':
				self.__items.append(buffer)
			return len(self.__items)
		except BaseException as e:
			return e
	def rearrange(self:object) -> int|BaseException:
		pattern, count = self.__prefix + b"\\d+" + self.__suffix, 0
		for idx in range(len(self.__items) - 1, -1, -1):
			iters = tuple(finditer(pattern, self.__items[idx]))
			if len(iters) >= 1:
				startIdx, endIdx = iters[0].start(), iters[0].end()
				count += 1
				target = self.__prefix + str(count).encode("utf-8") + self.__suffix
				self.__items[idx] = self.__items[idx][:startIdx] + target + self.__items[idx][endIdx:]
		return count
	def writeFile(self:object, filePath:str = "output.ndjson") -> int|BaseException:
		try:
			with open(filePath, "wb") as f:
				for item in self.__items:
					f.write(item + b"\n")
			return len(self.__items)
		except BaseException as e:
			return e


def main() -> int:
	# Parameters #
	originalNdjsonFilePath, targetNdjsonFilePath = "messages.ndjson", "output.ndjson"
	rearranger = Rearranger()
	
	# Reading #
	readCount = rearranger.readFile(originalNdjsonFilePath)
	if isinstance(readCount, int):
		print("Successfully loaded {0} item(s) from \"{1}\". ".format(readCount, originalNdjsonFilePath))
	else:
		print("Failed to read \"{0}\". Details are as follows. \n\t{1}".format(originalNdjsonFilePath, "The program is interrupted by users. " if isinstance(readCount, KeyboardInterrupt) else readCount))
		exitCode = EOF
		try:
			print("Please press the enter key to exit ({0}). ".format(exitCode))
			input()
		except:
			print()
		return exitCode
	
	# Rearranging #
	rearrangedCount = rearranger.rearrange()
	if isinstance(rearrangedCount, int):
		print("Successfully rearranged {0} item(s). ".format(rearrangedCount))
	else:
		print("Failed to rearrange. Details are as follows. \n\t{0}".format("The program is interrupted by users. " if isinstance(rearrangedCount, KeyboardInterrupt) else rearrangedCount))
		exitCode = EXIT_FAILURE
		try:
			print("Please press the enter key to exit ({0}). ".format(exitCode))
			input()
		except:
			print()
		return exitCode
	
	# Writing #
	writtenCount = rearranger.writeFile(targetNdjsonFilePath)
	if isinstance(writtenCount, int):
		print("Successfully wrote {0} item(s) to \"{1}\". ".format(writtenCount, targetNdjsonFilePath))
	else:
		print("Failed to write to \"{0}\". Details are as follows. \n\t{1}".format(targetNdjsonFilePath, "The program is interrupted by users. " if isinstance(writtenCount, KeyboardInterrupt) else writtenCount))
		exitCode = EOF
		try:
			print("Please press the enter key to exit ({0}). ".format(exitCode))
			input()
		except:
			print()
		return exitCode
	
	# Returning #
	exitCode = EXIT_SUCCESS if isinstance(rearrangedCount, int) and readCount == rearrangedCount == writtenCount else EXIT_FAILURE
	try:
		print("Please press the enter key to exit ({0}). ".format(exitCode))
		input()
	except:
		print()
	return exitCode



if "__main__" == __name__:
	exit(main())