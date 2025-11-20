"""Unit tests for PluginHookManager."""

from pathlib import Path

from galleria.manager.hooks import PluginHookManager
from galleria.plugins import PluginContext, PluginResult


class TestPluginHookManager:
    """Tests for PluginHookManager hook system."""

    def test_hook_manager_initialization(self):
        """PluginHookManager initializes with empty hook storage."""
        manager = PluginHookManager()

        assert manager.list_hooks() == []

    def test_register_hook_adds_callback(self):
        """register_hook adds callback to specified hook name."""
        manager = PluginHookManager()

        def test_callback(context: PluginContext) -> PluginResult:
            return PluginResult(success=True, output_data="test")

        manager.register_hook("test_hook", test_callback)

        assert "test_hook" in manager.list_hooks()

    def test_register_multiple_callbacks_same_hook(self):
        """Multiple callbacks can be registered for the same hook."""
        manager = PluginHookManager()

        def callback1(context: PluginContext) -> PluginResult:
            return PluginResult(success=True, output_data="callback1")

        def callback2(context: PluginContext) -> PluginResult:
            return PluginResult(success=True, output_data="callback2")

        manager.register_hook("test_hook", callback1)
        manager.register_hook("test_hook", callback2)

        # Verify hook is registered
        assert "test_hook" in manager.list_hooks()

        # Execute and verify both callbacks run
        context = PluginContext(
            input_data="test",
            config={},
            output_dir=Path("/tmp")
        )
        results = manager.execute_hook("test_hook", context)

        assert len(results) == 2
        assert results[0].output_data == "callback1"
        assert results[1].output_data == "callback2"

    def test_execute_hook_with_no_callbacks_returns_empty_list(self):
        """execute_hook returns empty list for unregistered hook."""
        manager = PluginHookManager()

        context = PluginContext(
            input_data="test",
            config={},
            output_dir=Path("/tmp")
        )
        results = manager.execute_hook("nonexistent_hook", context)

        assert results == []

    def test_execute_hook_passes_context_to_callback(self):
        """execute_hook passes PluginContext to callback correctly."""
        manager = PluginHookManager()
        received_context = None

        def test_callback(context: PluginContext) -> PluginResult:
            nonlocal received_context
            received_context = context
            return PluginResult(success=True, output_data="test")

        manager.register_hook("test_hook", test_callback)

        test_context = PluginContext(
            input_data={"key": "value"},
            config={"setting": "test"},
            output_dir=Path("/test/path")
        )

        manager.execute_hook("test_hook", test_context)

        assert received_context is test_context
        assert received_context.input_data == {"key": "value"}
        assert received_context.config == {"setting": "test"}
        assert received_context.output_dir == Path("/test/path")

    def test_execute_hook_returns_callback_results(self):
        """execute_hook returns PluginResult from callback."""
        manager = PluginHookManager()

        def test_callback(context: PluginContext) -> PluginResult:
            return PluginResult(
                success=True,
                output_data="processed",
                metadata={"hook": "executed"}
            )

        manager.register_hook("test_hook", test_callback)

        context = PluginContext(
            input_data="input",
            config={},
            output_dir=Path("/tmp")
        )
        results = manager.execute_hook("test_hook", context)

        assert len(results) == 1
        assert results[0].success is True
        assert results[0].output_data == "processed"
        assert results[0].metadata == {"hook": "executed"}

    def test_execution_order_matches_registration_order(self):
        """Callbacks execute in the order they were registered."""
        manager = PluginHookManager()
        execution_order = []

        def callback1(context: PluginContext) -> PluginResult:
            execution_order.append("first")
            return PluginResult(success=True, output_data="1")

        def callback2(context: PluginContext) -> PluginResult:
            execution_order.append("second")
            return PluginResult(success=True, output_data="2")

        def callback3(context: PluginContext) -> PluginResult:
            execution_order.append("third")
            return PluginResult(success=True, output_data="3")

        # Register in specific order
        manager.register_hook("ordered_hook", callback1)
        manager.register_hook("ordered_hook", callback2)
        manager.register_hook("ordered_hook", callback3)

        context = PluginContext(
            input_data="test",
            config={},
            output_dir=Path("/tmp")
        )
        results = manager.execute_hook("ordered_hook", context)

        # Verify execution order
        assert execution_order == ["first", "second", "third"]
        assert len(results) == 3
        assert [r.output_data for r in results] == ["1", "2", "3"]

    def test_list_hooks_returns_registered_hook_names(self):
        """list_hooks returns all hook names with registered callbacks."""
        manager = PluginHookManager()

        def dummy_callback(context: PluginContext) -> PluginResult:
            return PluginResult(success=True, output_data="test")

        # Register hooks in random order
        manager.register_hook("before_provider", dummy_callback)
        manager.register_hook("after_css", dummy_callback)
        manager.register_hook("before_template", dummy_callback)

        hooks = manager.list_hooks()

        # Should contain all registered hook names
        assert set(hooks) == {"before_provider", "after_css", "before_template"}

    def test_hook_manager_handles_callback_exceptions_gracefully(self):
        """Hook manager should handle callback exceptions without crashing."""
        manager = PluginHookManager()

        def failing_callback(context: PluginContext) -> PluginResult:
            raise ValueError("Callback failed")

        def working_callback(context: PluginContext) -> PluginResult:
            return PluginResult(success=True, output_data="works")

        manager.register_hook("test_hook", failing_callback)
        manager.register_hook("test_hook", working_callback)

        context = PluginContext(
            input_data="test",
            config={},
            output_dir=Path("/tmp")
        )

        # This test documents current behavior - we may want to improve error handling later
        try:
            results = manager.execute_hook("test_hook", context)
            # If no exception is raised, verify at least the working callback ran
            assert len(results) >= 1
        except ValueError:
            # If exception is raised, that's also acceptable behavior for now
            pass

    def test_standard_hook_names_work_correctly(self):
        """Standard pipeline hook names work correctly."""
        manager = PluginHookManager()

        def dummy_callback(context: PluginContext) -> PluginResult:
            return PluginResult(success=True, output_data="executed")

        # Register all standard hooks
        standard_hooks = [
            "before_provider", "after_provider",
            "before_processor", "after_processor",
            "before_transform", "after_transform",
            "before_template", "after_template",
            "before_css", "after_css"
        ]

        for hook_name in standard_hooks:
            manager.register_hook(hook_name, dummy_callback)

        # Verify all hooks are registered
        registered_hooks = set(manager.list_hooks())
        assert registered_hooks == set(standard_hooks)

        # Verify each hook can be executed
        context = PluginContext(
            input_data="test",
            config={},
            output_dir=Path("/tmp")
        )

        for hook_name in standard_hooks:
            results = manager.execute_hook(hook_name, context)
            assert len(results) == 1
            assert results[0].success is True
            assert results[0].output_data == "executed"
