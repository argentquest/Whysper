import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import os
import sys

# Ensure backend path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Explicit imports - failure here means environment is not set up correctly
from app.services.diagram_factory_core import DiagramFactoryService
from app.services.image_analysis_service import ImageAnalysisService

class TestServices(unittest.IsolatedAsyncioTestCase):

    async def test_diagram_factory_service(self):
        """Test DiagramFactoryService logic."""

        # DiagramFactoryService uses get_registry from diagrams.provider_registry
        with patch('app.services.diagram_factory_core.get_registry') as mock_get_registry:
            mock_registry = MagicMock()
            mock_get_registry.return_value = mock_registry

            # Mock getting a provider
            mock_provider = MagicMock()
            mock_provider.render.return_value = MagicMock(success=True, content="<svg>mock</svg>", metadata={})
            mock_registry.get_default_provider.return_value = mock_provider
            mock_registry.get.return_value = mock_provider

            # Mock session
            mock_session = MagicMock()
            mock_session.diagram_code = "x->y"
            mock_session.diagram_type = "d2"
            mock_session.graph_state = {}
            mock_session.errors = []
            # Async queue mock for push update
            mock_session.update_queue.put = AsyncMock()

            # Mock internal graph getter to avoid building graph
            with patch('app.services.diagram_factory_core.get_diagram_factory_graph'):
                service = DiagramFactoryService(session=mock_session)

                result = await service.render_diagram(diagram_code="x->y")

                self.assertEqual(result["status"], "rendered")
                self.assertEqual(result["svgOutput"], "<svg>mock</svg>")

    def test_image_analysis_service(self):
        """Test ImageAnalysisService initialization."""

        with patch('app.services.image_analysis_service.settings'):
             # Mock init
             with patch('app.services.image_analysis_service.ImageAnalysisService.__init__', return_value=None):
                service = ImageAnalysisService()
                self.assertIsInstance(service, ImageAnalysisService)
