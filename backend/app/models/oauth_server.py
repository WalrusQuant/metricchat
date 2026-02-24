"""OAuth 2.1 Authorization Server models.

Used when BOW acts as an OAuth Authorization Server for external MCP clients
like Claude Web. Not to be confused with OAuthAccount which stores BOW's
OAuth *client* credentials for SSO login providers.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseSchema


class OAuthMCPClient(BaseSchema):
    """A registered OAuth client (e.g., Claude Web) that can request access to the MCP API."""
    __tablename__ = "oauth_mcp_clients"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    client_id = Column(String(64), nullable=False, unique=True, index=True)
    client_secret_hash = Column(String(64), nullable=False)  # SHA-256
    name = Column(String(255), nullable=False)  # e.g. "Claude Web"
    redirect_uris = Column(Text, nullable=False)  # JSON array of allowed redirect URIs
    scopes = Column(String(255), nullable=False, default="mcp")

    organization = relationship("Organization")


class OAuthMCPAuthorizationCode(BaseSchema):
    """Short-lived authorization code issued during the OAuth consent flow."""
    __tablename__ = "oauth_mcp_authorization_codes"

    code = Column(String(128), nullable=False, unique=True, index=True)
    client_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    redirect_uri = Column(String(2048), nullable=False)
    scope = Column(String(255), nullable=False, default="mcp")
    code_challenge = Column(String(128), nullable=False)  # PKCE S256
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User")
    organization = relationship("Organization")


class OAuthMCPAccessToken(BaseSchema):
    """Access and refresh tokens issued to OAuth clients for MCP API access."""
    __tablename__ = "oauth_mcp_access_tokens"

    token_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256
    client_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    scope = Column(String(255), nullable=False, default="mcp")
    expires_at = Column(DateTime, nullable=False)
    refresh_token_hash = Column(String(64), nullable=True, unique=True, index=True)  # SHA-256
    refresh_expires_at = Column(DateTime, nullable=True)

    user = relationship("User")
    organization = relationship("Organization")
