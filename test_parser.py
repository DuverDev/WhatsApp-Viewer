import unittest

from parser import parse_whatsapp_backup, filter_messages


class ParseWhatsappBackupTests(unittest.TestCase):
    def test_parses_basic_whatsapp_lines(self):
        content = "12/10/2024, 20:15 - Ana: Hola\n12/10/2024, 20:18 - Tú: Qué tal?"
        messages = parse_whatsapp_backup(content)
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].sender, "Ana")
        self.assertEqual(messages[1].text, "Qué tal?")

    def test_filters_by_text_and_sender_and_date(self):
        content = (
            "12/10/2024, 20:15 - Ana: Hola\n"
            "13/10/2024, 09:00 - Juan: Reunión\n"
            "13/10/2024, 09:30 - Ana: Cambio de hora"
        )
        messages = parse_whatsapp_backup(content)

        filtered = filter_messages(messages, sender="Ana", search="hora", start_date="13/10/2024", end_date="13/10/2024")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].sender, "Ana")
        self.assertIn("hora", filtered[0].text.lower())

    def test_parses_real_export_format_with_ampm_and_system_messages(self):
        content = (
            "28/8/2021, 8:18 a. m. - Los mensajes y las llamadas están cifrados de extremo a extremo. Nadie fuera de este chat, ni siquiera WhatsApp, puede leerlos ni escucharlos. Toca para obtener más información.\n"
            "28/8/2021, 8:18 a. m. - Contacto Demo 💙: Hola\n"
            "28/8/2021, 8:19 a. m. - 💙 Usuario B: Hola, tiempo sin hablar"
        )
        messages = parse_whatsapp_backup(content)
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0].sender, "Sistema")
        self.assertEqual(messages[1].sender, "Contacto Demo 💙")
        self.assertEqual(messages[2].sender, "💙 Usuario B")

    def test_parses_english_android_format_with_attachments_and_omitted(self):
        content = (
            "10/14/24, 9:30 AM - Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them. Tap to learn more.\n"
            "10/14/24, 9:31 AM - John: Hey there!\n"
            "10/14/24, 9:32 AM - You: Hi John, check this out\n"
            "10/14/24, 9:33 AM - You: IMG-20241014-WA0001.jpg (file attached)\n"
            "10/14/24, 9:34 AM - John: <Media omitted>"
        )
        messages = parse_whatsapp_backup(content)
        self.assertEqual(len(messages), 5)
        self.assertEqual(messages[0].sender, "Sistema")
        self.assertEqual(messages[1].sender, "John")
        self.assertEqual(messages[1].text, "Hey there!")
        self.assertEqual(messages[2].sender, "You")
        self.assertEqual(messages[3].media_type, "image")
        self.assertEqual(messages[3].media_file, "IMG-20241014-WA0001.jpg")
        self.assertEqual(messages[4].media_type, "omitted")

    def test_parses_ios_bracketed_format_with_seconds_and_unicode_marks(self):
        content = (
            "\u200e[12/31/23, 11:59:02 PM] Messages and calls are end-to-end encrypted.\n"
            "[12/31/23, 11:59:45 PM] Alice: Happy New Year! 🎉\n"
            "[01/01/24, 12:00:10 AM] Bob: <attached: 00000001-PHOTO-2024-01-01.jpg>\n"
            "[01/01/24, 12:01:05 AM] Alice: Awesome picture!"
        )
        messages = parse_whatsapp_backup(content)
        self.assertEqual(len(messages), 4)
        self.assertEqual(messages[0].sender, "Sistema")
        self.assertEqual(messages[1].sender, "Alice")
        self.assertEqual(messages[1].text, "Happy New Year! 🎉")
        self.assertEqual(messages[2].sender, "Bob")
        self.assertEqual(messages[2].media_type, "image")
        self.assertEqual(messages[2].media_file, "00000001-PHOTO-2024-01-01.jpg")
        self.assertEqual(messages[3].sender, "Alice")

    def test_multiline_messages_in_english(self):
        content = (
            "10/14/24, 10:00 AM - John: First line of the message\n"
            "Second line of the message\n"
            "Third line of the message\n"
            "10/14/24, 10:02 AM - You: Got it!"
        )
        messages = parse_whatsapp_backup(content)
        self.assertEqual(len(messages), 2)
        self.assertIn("Second line of the message", messages[0].text)
        self.assertIn("Third line of the message", messages[0].text)
        self.assertEqual(messages[1].text, "Got it!")


if __name__ == "__main__":
    unittest.main()
