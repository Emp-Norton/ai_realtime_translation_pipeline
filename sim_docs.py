import serial
import time
import os

from openai import OpenAI
from decouple import config

oaikey = config('OAIKEY')

class SIM800Module:
	def __init__(self, port="/dev/serial0", baudrate=115000):
		"""
        Initializes a SIM800 module object.

		Parameters:
		port (str): The serial port to use for communication. Default is "/dev/serial0".
		baudrate (int): The baud rate to use for communication. Default is 115000.
		"""
		self.port = port
		self.engageAi = False
		self.baudrate = baudrate
		self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
		self.isConnected = False

	def connect(self):
		"""
		Connects to the SIM800 module.
		Attempts to open the serial connection and send an "AT" command to the module. If the response contains "OK", the connection is considered successful.
        """
		if not self.ser.is_open:
			self.ser.open()
			self.ser.write(b"AT\r\n")
			response = self.ser.readlines()
			print(response)
			if "OK" in str(response):
				self.isConnected = True
				print("Connected to SIM800 module.")
			else:
				print("Failed to connect to SIM800 module.")
		else:
			self.isConnected=True
			print("Possibly already connected.")

	def check_status(self):
		"""
		Checks status of connection between RPI and Sim Module. Takes no arguments.
		"""
		if self.isConnected:
			self.ser.write(b"AT+CSQ\r\n")
			response = self.ser.readlines()
			print("Signal Quality: ", response[1].decode("utf-8").strip())
		else:
			print("Not connected to SIM800 module.")

	def send_message(self, recipient_number, message):
		"""
		Sends a message to a recipient.

		Parameters:
		recipient_number (str): The phone number of the recipient.
		message (str): The message to be sent.
		"""
		if self.isConnected:
			self.ser.write(b"AT+CMGF=1\r\n")
			time.sleep(0.5)
			self.ser.write(b'AT+CMGS="' + recipient_number.encode() + b'"\r\n')
			time.sleep(0.5)
			self.ser.write(message.encode() + b"\r\n")
			time.sleep(0.5)
			self.ser.write(b"\x1A")
			response = self.ser.readlines()
			if "OK" in str(response):
				print("Message sent successfully.")
			else:
				print("Failed to send message.")
		else:
			print("Not connected to SIM800 module.")

	def read_messages(self):
		"""
		Reads all messages from the SIM800 module.

		Returns:
		list: A list of messages read from the module.
		"""
		message_pile = []
		if self.isConnected:
			self.ser.write(b'AT+CMGL="ALL"\r\n')
			response = self.ser.readlines()
			for line in response:
				cleaned_line = line.decode("utf-8").strip()
				print(cleaned_line)
				message_pile.append(cleaned_line)
		else:
			print("Not connected to SIM800 module.")
		return message_pile

	def delete_message(self, index):
		"""
		Deletes a message at a specified index.

		Parameters:
		index (int): The index of the message to be deleted.
		"""
		if self.isConnected:
			self.ser.write(b"AT+CMGD=" + str(index).encode() + b"\r\n")
			response = self.ser.readlines()
			if "OK" in str(response):
				print("Message deleted successfully.")
			else:
				print("Failed to delete message.")
		else:
			print("Not connected to SIM800 module.")

	def disconnect(self):
		"""
		Disconnects from the SIM800 module.
		"""
		if self.isConnected:
			self.ser.close()
			self.isConnected = False
			print("Disconnected from SIM800 module.")
		else:
			print("Not connected to SIM800 module.")


class OpenAIFormatter:
	def __init__(self, key=oaikey, model='gpt-4-turbo'):
		"""
		Initializes an OpenAI formatter object.

	Parameters:
	key (str): The OpenAI API key. Default is the value of the OAIKEY environment variable.
	model (str): The OpenAI model to use. Default is 'gpt-4-turbo'.
	"""
		self.model = model
		self.client = self._handle_credentials(key)

	def _handle_credentials(self, key):
		"""
		Handles OpenAI credentials.

		Parameters:
		key (str): The OpenAI API key.

		Returns:
		OpenAI: An OpenAI client object.
		"""
		return OpenAI(api_key=key)

	def format_prompt(self, message, **kwargs):
		"""
		Formats a prompt for OpenAI.

		Parameters:
		message (str): The message to be formatted.

		Returns:
		dict: A dictionary containing the formatted prompt.
		"""
		msg_obj = {'role':'user', 'content':message}
		return msg_obj

	def send_prompt(self, prompt):
		"""
		Sends a prompt to OpenAI.

		Parameters:
		prompt (str): The prompt to be sent.

		Returns:
		str: The response from OpenAI.
		"""
		formatted_msg = self.format_prompt(prompt)
		r = self.client.chat.completions.create(model=self.model,messages=[formatted_msg])
		return r.choices[0].message.content


if __name__ == "main":
	sim_module = SIM800Module()
	sim_module.connect()
	sim_module.check_status()
	formatter = OpenAIFormatter()

	while True and sim_module.isConnected:
		messages = sim_module.read_messages()
		while len(messages) > 0:
			if sim_module.engageAI:
				llm_responses = formatter.send_prompt(messages.pop())
				print(f"Sending {llm_responses}")
				if llm_responses is not None:
					sim_module.send_message("+14159646380", llm_responses)