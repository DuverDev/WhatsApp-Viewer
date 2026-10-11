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
            "28/8/2021, 8:18 a. m. - Nora Bonita 💙: Hola\n"
            "28/8/2021, 8:19 a. m. - 💙 Blacktao: Hola, tiempo sin hablar"
        )
        messages = parse_whatsapp_backup(content)
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0].sender, "Sistema")
        self.assertEqual(messages[1].sender, "Nora Bonita 💙")
        self.assertEqual(messages[2].sender, "💙 Blacktao")


if __name__ == "__main__":
    unittest.main()
