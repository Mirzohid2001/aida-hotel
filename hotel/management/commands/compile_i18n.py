import re
from pathlib import Path

from django.core.management.base import BaseCommand

from hotel.i18n.strings import TRANSLATIONS


class Command(BaseCommand):
    help = "Fill locale PO files with translations and compile messages"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parents[3]
        for lang in ("uz", "ru", "en"):
            po_path = base_dir / "locale" / lang / "LC_MESSAGES" / "django.po"
            if not po_path.exists():
                self.stderr.write(f"Missing {po_path}")
                continue
            content = po_path.read_text(encoding="utf-8")
            content = self._fill_translations(content, lang)
            content = content.replace('"Language: \\n"', f'"Language: {lang}\\n"')
            content = content.replace("#, fuzzy\n", "")
            po_path.write_text(content, encoding="utf-8")
            self.stdout.write(f"Updated {po_path}")

        from django.core.management import call_command

        call_command("compilemessages", verbosity=1)
        self.stdout.write(self.style.SUCCESS("Translations compiled."))

    def _fill_translations(self, content: str, lang: str) -> str:
        def replace_block(match):
            msgid = match.group(1)
            if msgid not in TRANSLATIONS:
                return match.group(0)
            msgstr = TRANSLATIONS[msgid][lang]
            return f'msgid "{self._escape(msgid)}"\nmsgstr "{self._escape(msgstr)}"'

        # Single-line msgid/msgstr pairs
        pattern = r'msgid "((?:\\.|[^"\\])*)"\nmsgstr ""'
        content = re.sub(pattern, replace_block, content)

        # Multi-line msgid
        multiline_pattern = r'msgid ""\n"((?:[^"]|\n)*)"\nmsgstr ""'
        def replace_multiline(match):
            lines = match.group(1).replace('"\n"', "")
            msgid = lines.replace("\\n", "\n")
            if msgid not in TRANSLATIONS:
                return match.group(0)
            msgstr = TRANSLATIONS[msgid][lang]
            escaped = self._escape(msgstr)
            if "\n" in msgstr:
                parts = escaped.split("\\n")
                msgstr_block = 'msgstr ""\n' + "\n".join(f'"{p}\\n"' for p in parts[:-1])
                if parts[-1]:
                    msgstr_block += f'\n"{parts[-1]}"'
                return f'msgid ""\n"{lines}"\n{msgstr_block}'
            return f'msgid ""\n"{lines}"\nmsgstr "{escaped}"'

        content = re.sub(multiline_pattern, replace_multiline, content)
        return content

    @staticmethod
    def _escape(text: str) -> str:
        return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
