import json
from pathlib import Path
from doc_flesh.models import SiteInfo, SiteCategory
import questionary

def handle_existing_siteinfo(siteinfo_path: Path) -> SiteInfo:
    """Handle existing siteinfo.json file or provide empty with defaults."""

    # Offer parent directory as the slug, as this is usually the repository name, which is
    # usually in the <repo>.github.io/ URL.
    default_site_slug = siteinfo_path.parent.name

    if siteinfo_path.exists():
        print("[INFO] Siteinfo exists. Appending...")
        existing_data = json.loads(siteinfo_path.read_text())

        # Use Pydantic's construct to bypass validation and fill missing fields with defaults
        siteinfo = SiteInfo.model_construct(**existing_data)
        siteinfo = SiteInfo(
            site_name=existing_data.get("site_name", ""),
            site_name_slug=existing_data.get("site_name_slug", default_site_slug),
            site_uses_mathjax=existing_data.get("site_uses_mathjax", False),
            site_uses_precommit=existing_data.get("site_uses_precommit", False),
            category=existing_data.get("category", SiteCategory.learning_tools),
            related_repo=existing_data.get("related_repo", None)
        )
    else:
        print("[INFO] No existing siteinfo found. Creating a new one...")
        siteinfo = SiteInfo(
            site_name="",
            site_name_slug=default_site_slug,
            site_uses_mathjax=False,
            site_uses_precommit=False,
            category=SiteCategory.learning_tools,
            related_repo=""
        )
    return siteinfo
        

def questionnaire(siteinfo: SiteInfo) -> SiteInfo:
    """Generate or update the siteinfo.json file in the current directory."""

    # Site name
    siteinfo.site_name = questionary.text(
        "Site name:",
        default=siteinfo.site_name or "My Site"
    ).ask()

    # Slug
    siteinfo.site_name_slug = questionary.text(
        "Site name slug:",
        default=siteinfo.site_name_slug or "my-site"
    ).ask()

    # Category
    category_str = questionary.select(
        "Category:",
        choices=[c.value for c in SiteCategory],
        default=siteinfo.category.value if isinstance(siteinfo.category, SiteCategory) else siteinfo.category
    ).ask()
    # Convert the string back to enum to avoid validation warnings
    siteinfo.category = next((c for c in SiteCategory if c.value == category_str), SiteCategory.learning_tools)

    siteinfo.site_uses_mathjax = questionary.confirm(
        "Does the site use MathJax?",
        default=siteinfo.site_uses_mathjax
    ).ask()

    siteinfo.site_uses_precommit = questionary.confirm(
        "Does the site use pre-commit?",
        default=siteinfo.site_uses_precommit
    ).ask()

    # Related repo link
    siteinfo.related_repo = questionary.text(
        "Related repo (Markdown link):",
        default=siteinfo.related_repo or "[Example](https://example.com)"
    ).ask()

    return siteinfo

def write_siteinfo(siteinfo: SiteInfo, path: Path):
    """Write the siteinfo.json file to the given path"
    """

    # Display the to-be-written file
    print("[INFO] Siteinfo to be written:")
    siteinfo_json = siteinfo.model_dump_json(indent=2)
    print(siteinfo_json)

    # Verify that the user wants to write the file
    confirm = questionary.confirm("Write the siteinfo.json file?").ask()
    if not confirm:
        print("[INFO] Aborted.")
        return

    path.write_text(siteinfo_json)
    print(f"[INFO] Siteinfo written to {path}")


def generate_and_write_siteinfo(path: Path):
    """Generate and write the siteinfo.json file to the given path."""
    # To absolute path
    siteinfo_dir = Path(path).expanduser().resolve()
    siteinfo_path = siteinfo_dir / "siteinfo.json"

    # Take all three steps
    siteinfo = handle_existing_siteinfo(siteinfo_path)
    user_filled_siteinfo = questionnaire(siteinfo)
    write_siteinfo(user_filled_siteinfo, siteinfo_path)