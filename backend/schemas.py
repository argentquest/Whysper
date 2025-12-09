"""Pydantic schemas for the web backend."""

from __future__ import annotations

from typing import List, Optional, Any, Dict

from pydantic import BaseModel, Field, ConfigDict


class ConversationMessageModel(BaseModel):
    role: str
    content: str


class QuestionStatusModel(BaseModel):
    question: str
    status: str
    response: str = ""
    timestamp: str = ""
    tokens_used: int = Field(default=0, alias="tokensUsed")
    processing_time: float = Field(default=0.0, alias="processingTime")
    model_used: str = Field(default="", alias="modelUsed")

    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())


class ConversationSummaryModel(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    provider: str
    selected_model: str = Field(alias="selectedModel")
    selected_directory: str = Field(alias="selectedDirectory")
    selected_files: List[str] = Field(alias="selectedFiles")
    persistent_files: List[str] = Field(alias="persistentFiles")
    question_history: List[QuestionStatusModel] = Field(alias="questionHistory")
    conversation_history: List[ConversationMessageModel] = Field(alias="conversationHistory")

    model_config = ConfigDict(populate_by_name=True)


class ConversationCreateRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = Field(default=None, alias="apiKey")
    access_key: Optional[str] = Field(default=None, alias="accessKey")

    model_config = ConfigDict(populate_by_name=True)


class ConversationCreateResponse(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    provider: str
    model: str
    available_models: List[str] = Field(alias="availableModels")
    summary: ConversationSummaryModel

    model_config = ConfigDict(populate_by_name=True)


class ConversationIdResponse(BaseModel):
    conversation_id: str = Field(alias="conversationId")


class AskQuestionRequest(BaseModel):
    question: str
    selected_files: Optional[List[str]] = Field(default=None, alias="selectedFiles")
    persistent: bool = False

    model_config = ConfigDict(populate_by_name=True)


class AskQuestionResponse(BaseModel):
    rawResponse: str = Field(alias="rawResponse")
    response: str
    processing_time: float = Field(alias="processingTime")
    tokens_used: int = Field(alias="tokensUsed")
    question_index: int = Field(alias="questionIndex")
    summary: ConversationSummaryModel

    model_config = ConfigDict(populate_by_name=True)


class SystemPromptResponse(BaseModel):
    response: str
    processing_time: float = Field(alias="processingTime")
    tokens_used: int = Field(alias="tokensUsed")
    summary: ConversationSummaryModel

    model_config = ConfigDict(populate_by_name=True)


class SetDirectoryRequest(BaseModel):
    path: str


class SetDirectoryResponse(BaseModel):
    directory: str
    files: List[dict]
    message: str
    summary: ConversationSummaryModel


class UpdateFilesRequest(BaseModel):
    selected_files: List[str] = Field(alias="selectedFiles")
    persistent: bool = False

    model_config = ConfigDict(populate_by_name=True)


class ExportConversationResponse(BaseModel):
    summary: ConversationSummaryModel


class ImportConversationRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = Field(default=None, alias="apiKey")
    conversation_history: List[ConversationMessageModel] = Field(alias="conversationHistory")
    question_history: List[QuestionStatusModel] = Field(alias="questionHistory")
    selected_files: List[str] = Field(default_factory=list, alias="selectedFiles")
    persistent_files: List[str] = Field(default_factory=list, alias="persistentFiles")
    selected_directory: Optional[str] = Field(default=None, alias="selectedDirectory")

    model_config = ConfigDict(populate_by_name=True)


class SettingsUpdateRequest(BaseModel):
    updates: dict


class SystemMessageUpdateRequest(BaseModel):
    filename: str
    content: str


class SystemMessageSetRequest(BaseModel):
    filename: str


class FileContentRequest(BaseModel):
    files: List[str]


class FileContentResponse(BaseModel):
    combined_content: str = Field(alias="combinedContent")


class DirectoryScanRequest(BaseModel):
    path: str


class DirectoryScanResponse(BaseModel):
    directory: str
    files: List[dict]
    tree: dict


class GitHubImportRequest(BaseModel):
    """
    Request schema for importing a public GitHub repository.

    This model validates and normalizes the user's request to import a GitHub
    repository for Set Context usage. It supports multiple repository identifier
    formats and allows specifying a git reference and optional subpath.

    Attributes:
        repository: Repository identifier in one of these formats:
            - Short form: "owner/repo" (e.g., "facebook/react")
            - HTTPS URL: "https://github.com/owner/repo"
            - HTTPS URL with .git: "https://github.com/owner/repo.git"
        ref: Git reference to fetch. Can be:
            - Branch name (e.g., "main", "develop")
            - Tag (e.g., "v1.0.0", "2023.12")
            - Commit SHA (full or abbreviated)
            Defaults to "main" if not specified.
        subpath: Optional subdirectory path within the repository to limit
            the scan scope. For example, "packages/react" or "src/components".
            Must exist within the repository and cannot escape the repo root.

    Example:
        >>> request = GitHubImportRequest(
        ...     repository="python/cpython",
        ...     ref="3.11",
        ...     subpath="Lib/collections"
        ... )
    """
    repository: str = Field(
        ...,
        description="Repository in owner/repo form or a GitHub URL",
        examples=["facebook/react", "https://github.com/python/cpython"]
    )
    ref: Optional[str] = Field(
        default="main",
        description="Branch, tag, or commit SHA to fetch (default: main)",
        examples=["main", "v18.2.0", "3.11.0"]
    )
    subpath: Optional[str] = Field(
        default=None,
        description="Optional subdirectory within the repo to limit scan scope",
        examples=["packages/react", "src/lib", "Lib/collections"]
    )

    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())


class GitHubImportResponse(BaseModel):
    """
    Response schema for a successful GitHub repository import.

    This model provides all the information needed for the Set Context UI
    to display and select files from the imported repository. The structure
    mirrors the response from local directory scanning for consistency.

    Attributes:
        repository: Normalized repository identifier in "owner/name" format.
        ref: Git reference (branch/tag/commit) that was actually fetched.
        rootPath: Absolute local filesystem path to the repository root.
            This is the cached location where the tarball was extracted.
        scanPath: Absolute local filesystem path that was scanned.
            May be the same as rootPath, or a subdirectory if subpath was specified.
        files: List of file metadata dictionaries, each containing:
            - path: File path (relative or absolute)
            - name: File name
            - size: File size in bytes
            - Additional fields from FileService.scan_directory
        tree: Hierarchical directory tree structure with:
            - name: Node name
            - type: "file" or "directory"
            - children: List of child nodes (for directories)
            - Additional fields from FileService.build_directory_tree
        message: User-friendly success message describing what was loaded.

    Example:
        >>> response = GitHubImportResponse(
        ...     repository="python/cpython",
        ...     ref="3.11",
        ...     rootPath="/cache/python/cpython/3.11",
        ...     scanPath="/cache/python/cpython/3.11/Lib",
        ...     files=[...],
        ...     tree={...},
        ...     message="Loaded python/cpython@3.11 from GitHub"
        ... )

    Frontend Usage:
        The frontend can consume this response directly:
        - Display files in FileTreeModal for selection
        - Show the tree structure for hierarchical navigation
        - Use scanPath to indicate the context source
        - Display message to confirm successful import
    """
    repository: str = Field(description="Repository in owner/name format")
    ref: str = Field(description="Git reference that was fetched")
    rootPath: str = Field(
        alias="rootPath",
        description="Local filesystem path to repository root"
    )
    scanPath: str = Field(
        alias="scanPath",
        description="Local filesystem path that was scanned"
    )
    files: List[dict] = Field(
        description="List of file metadata dictionaries compatible with FileTreeModal"
    )
    tree: dict = Field(
        description="Hierarchical directory tree compatible with FileTreeModal"
    )
    message: str = Field(description="Success message for user display")

    model_config = ConfigDict(populate_by_name=True)


class ThemeToggleResponse(BaseModel):
    theme: str
    message: str


class ThemeSetRequest(BaseModel):
    theme: str


class UpdateModelRequest(BaseModel):
    model: str


class UpdateProviderRequest(BaseModel):
    provider: str
    api_key: Optional[str] = Field(default=None, alias="apiKey")
    models: Optional[List[str]] = None

    model_config = ConfigDict(populate_by_name=True)


class UpdateApiKeyRequest(BaseModel):
    api_key: str = Field(alias="apiKey")

    model_config = ConfigDict(populate_by_name=True)


class FolderInfo(BaseModel):
    path: str
    fileCount: int


class FolderFileCountRequest(BaseModel):
    path: str


class FolderFileCountResponse(BaseModel):
    folders: List[FolderInfo]


class TopFoldersResponse(BaseModel):
    folders: List[str]


class ChatRequest(BaseModel):
    message: str
    conversationId: Optional[str] = Field(default=None, alias="conversationId")
    contextFiles: Optional[List[str]] = Field(default=None, alias="contextFiles")
    settings: Optional[dict] = None

    model_config = ConfigDict(populate_by_name=True)


class ChatResponse(BaseModel):
    message: dict  # Message object with role, content, timestamp, etc.
    conversationId: str = Field(alias="conversationId")
    usage: Optional[dict] = None
    debug: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class CodeExtractionRequest(BaseModel):
    messageId: str = Field(..., description="ID of the message to extract code from")
    content: Optional[str] = Field(None, description="Optional content override")


class CodeExtractionResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    message: str


# Diagram Wizard Schemas
class DiagramStartRequest(BaseModel):
    initial_prompt: str
    diagram_type: str = "Mermaid"
    model_id: Optional[str] = None
    session_id: Optional[str] = None


class DiagramSessionResponse(BaseModel):
    session_id: str
    status: Dict[str, Any]
    message: str


class DiagramClarifyRequest(BaseModel):
    session_id: str
    response: str


class DiagramConfirmReadyRequest(BaseModel):
    session_id: str


class DiagramSelectTypeRequest(BaseModel):
    session_id: str
    diagram_type: str


class DiagramApproveRenderRequest(BaseModel):
    session_id: str


class DiagramRenderWizardRequest(BaseModel):
    session_id: str
    code: Optional[str] = None


class FileSaveRequest(BaseModel):
    path: str = Field(..., description="Relative path to the file to save")
    content: str = Field(..., description="File content to save")

    model_config = ConfigDict(populate_by_name=True)


class FileSaveResponse(BaseModel):
    success: bool
    message: str
    data: dict  # Contains path and size info

    model_config = ConfigDict(populate_by_name=True)


class FileReadResponse(BaseModel):
    success: bool
    data: dict  # Contains path, content, and size info

    model_config = ConfigDict(populate_by_name=True)


class FileCreateRequest(BaseModel):
    path: str = Field(..., description="Relative path for the new file")
    content: str = Field(default="", description="Initial file content (optional)")

    model_config = ConfigDict(populate_by_name=True)


class FileCreateResponse(BaseModel):
    success: bool
    message: str
    data: dict  # Contains path and size info

    model_config = ConfigDict(populate_by_name=True)


class FileUploadRequest(BaseModel):
    """Request model for file upload that bypasses local file system."""

    files: List[dict]  # List of file objects with name, content, and size
    target_directory: Optional[str] = Field(default="uploads", description="Target directory for uploaded files")

    model_config = ConfigDict(populate_by_name=True)


class FileUploadResponse(BaseModel):
    """Response model for file upload."""

    success: bool
    message: str
    data: dict  # Contains uploaded file paths and metadata

    model_config = ConfigDict(populate_by_name=True)


class UploadedFileItem(BaseModel):
    """Model for an uploaded file item that can be used in context."""

    path: str
    name: str
    size: int
    content: str  # File content as string
    type: str = "file"
    is_uploaded: bool = True  # Flag to indicate this is an uploaded file

    model_config = ConfigDict(populate_by_name=True)
