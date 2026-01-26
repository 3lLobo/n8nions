from typing import Any, Dict, List, Optional


class RoleTransformer:
    """Handles the transformation of role permissions between clusters."""

    def __init__(self, space_map: Dict[str, str]):
        self.space_map = space_map

    def transform(self, role_body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Applies mapping, wildcards, and exclusions to the role body.

        Returns:
            Modified dict, or None if the role should be excluded entirely.
        """
        if "applications" not in role_body:
            return role_body

        new_apps: List[Dict[str, Any]] = []

        for app in role_body["applications"]:
            # Only process Kibana application resources
            if not app.get("application", "").startswith("kibana"):
                new_apps.append(app)
                continue

            updated_resources: List[str] = []
            exclude_app = False

            for resource in app.get("resources", []):
                if not resource.startswith("space:"):
                    updated_resources.append(resource)
                    continue

                source_space = resource.replace("space:", "")
                mapping = self.space_map.get(source_space)

                if mapping == "!":
                    exclude_app = True
                    break  # Exclude this specific application block
                elif mapping == "*":
                    updated_resources.append("space:*")
                elif mapping:
                    updated_resources.append(f"space:{mapping}")
                else:
                    # Not in dict, copy as is
                    updated_resources.append(resource)

            if not exclude_app:
                app["resources"] = updated_resources
                new_apps.append(app)

        # If all application blocks were excluded, you might want to
        # return None or an empty list depending on your security needs.
        role_body["applications"] = new_apps
        return role_body
