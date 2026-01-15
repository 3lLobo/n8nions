from typing import Any, Dict, List, Optional
from elasticsearch import Elasticsearch
from config import AppConfig, ElasticConfig

class ElasticRoleManager:
    """
    A service class to manage and synchronize roles between Elasticsearch clusters.
    
    Attributes:
        client: The Elasticsearch client instance.
    """

    def __init__(self, config: ElasticConfig):
        """Initializes the client with the provided configuration."""
        self.client = Elasticsearch(
            hosts=[config.host],
            api_key=config.api_key
        )

    def get_role_permissions(self, role_name: str) -> Dict[str, Any]:
        """
        Retrieves permissions for a specific role.

        Args:
            role_name: The name of the role to fetch.

        Returns:
            A dictionary containing the role definition.

        Raises:
            Exception: If the role is not found or connection fails.
        """
        response = self.client.security.get_role(name=role_name)
        # Elastic returns { "role_name": { "cluster": [], ... } }
        return dict(response[role_name])

    def update_role(self, role_name: str, role_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates or updates a role in the cluster.

        Args:
            role_name: Name of the role to update.
            role_body: The permission body (cluster, indices, etc.).

        Returns:
            The API response from Elasticsearch.
        """
        # Clean up metadata that shouldn't be moved between clusters
        keys_to_filter: List[str] = ["metadata", "transient_metadata", "_status"]
        cleaned_body = {k: v for k, v in role_body.items() if k not in keys_to_filter}

        return self.client.security.put_role(name=role_name, **cleaned_body)

    def close(self) -> None:
        """Closes the connection to the cluster."""
        self.client.close()


class RoleSyncOrchestrator:
    """Orchestrates the data flow between two ElasticRoleManager instances."""

    def __init__(self, source_mgr: ElasticRoleManager, dest_mgr: ElasticRoleManager):
        self.source = source_mgr
        self.dest = dest_mgr

    def sync_role(self, role_name: str) -> None:
        """
        Executes the full sync process for a single role.
        
        Args:
            role_name: The role identifier to sync.
        """
        try:
            print(f"[*] Fetching permissions for: {role_name}")
            permissions = self.source.get_role_permissions(role_name)
            
            print(f"[*] Applying permissions to destination...")
            result = self.dest.update_role(role_name, permissions)
            
            print(f"[+] Successfully synced role: {role_name}")
        except Exception as e:
            print(f"[!] Sync failed for {role_name}: {str(e)}")

def main() -> None:
    """Main entry point for the automation script."""
    source_manager = ElasticRoleManager(AppConfig.SOURCE)
    dest_manager = ElasticRoleManager(AppConfig.DESTINATION)
    
    orchestrator = RoleSyncOrchestrator(source_manager, dest_manager)
    
    try:
        orchestrator.sync_role(AppConfig.ROLE_NAME)
    finally:
        source_manager.close()
        dest_manager.close()

if __name__ == "__main__":
    main()
