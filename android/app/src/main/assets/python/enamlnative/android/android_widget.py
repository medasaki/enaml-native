'''
Copyright (c) 2017, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on May 20, 2017

@author: jrm
'''
import jnius

from atom.api import Typed, Value, Coerced

from enaml.drag_drop import DropAction
from enaml.styling import StyleCache
from enaml.widgets.widget import Feature, ProxyWidget
from . import focus_registry
from .android_toolkit_object import AndroidToolkitObject

View = jnius.autoclass('android.view.View')

class AndroidWidget(AndroidToolkitObject, ProxyWidget):
    """ A Android implementation of an Enaml ProxyWidget.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(View)

    #: A private copy of the declaration features. This ensures that
    #: feature cleanup will proceed correctly in the event that user
    #: code modifies the declaration features value at runtime.
    _features = Coerced(Feature.Flags)

    #: Internal storage for the shared widget action.
    _widget_action = Value()

    #: Internal storage for the drag origin position.
    #_drag_origin = Typed(QPoint)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def init_widget(self):
        """ Initialize the underlying View object.

        """
        super(AndroidWidget, self).init_widget()
        widget = self.widget
        focus_registry.register(widget, self)
        self._setup_features()
        d = self.declaration
        if d.background:
            self.set_background(d.background)
        if d.foreground:
            self.set_foreground(d.foreground)
        if d.font:
            self.set_font(d.font)
        if -1 not in d.minimum_size:
            self.set_minimum_size(d.minimum_size)
        if -1 not in d.maximum_size:
            self.set_maximum_size(d.maximum_size)
        if d.tool_tip:
            self.set_tool_tip(d.tool_tip)
        if d.status_tip:
            self.set_status_tip(d.status_tip)
        if not d.enabled:
            self.set_enabled(d.enabled)
        self.refresh_style_sheet()
        # Don't make toplevel widgets visible during init or they will
        # flicker onto the screen. This applies particularly for things
        # like status bar widgets which are created with no parent and
        # then reparented by the status bar. Real top-level widgets must
        # be explicitly shown by calling their .show() method after they
        # are created.
        if widget.getParent() or not d.visible:
            self.set_visible(d.visible)
            
    def destroy(self):
        """ Destroy the underlying QWidget object.

        """
        self._teardown_features()
        focus_registry.unregister(self.widget)
        super(AndroidWidget, self).destroy()
        # If a QWidgetAction was created for this widget, then it has
        # taken ownership of the widget and the widget will be deleted
        # when the QWidgetAction is garbage collected. This means the
        # superclass destroy() method must run before the reference to
        # the QWidgetAction is dropped.
        del self._widget_action

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------

    def _setup_features(self):
        """ Setup the advanced widget feature handlers.

        """
        features = self._features = self.declaration.features
        if not features:
            return
        if features & Feature.FocusTraversal:
            self.hook_focus_traversal()
        if features & Feature.FocusEvents:
            self.hook_focus_events()
        if features & Feature.DragEnabled:
            self.hook_drag()
        if features & Feature.DropEnabled:
            self.hook_drop()

    def _teardown_features(self):
        """ Teardowns the advanced widget feature handlers.

        """
        features = self._features
        if not features:
            return
        if features & Feature.FocusTraversal:
            self.unhook_focus_traversal()
        if features & Feature.FocusEvents:
            self.unhook_focus_events()
        if features & Feature.DragEnabled:
            self.unhook_drag()
        if features & Feature.DropEnabled:
            self.unhook_drop()

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------
    def refresh_style_sheet(self):
        """ Refresh the widget style sheet with the current style data.

        """
        return # TODO: NOT IMPLEMENTED
        # parts = []
        # name = self.widget.objectName()
        # for style in StyleCache.styles(self.declaration):
        #     t = translate_style(name, style)
        #     if t:
        #         parts.append(t)
        # if len(parts) > 0:
        #     stylesheet = u'\n\n'.join(parts)
        # else:
        #     stylesheet = u''
        # self.widget.setStyleSheet(stylesheet)

    def tab_focus_request(self, reason):
        """ Handle a custom tab focus request.

        This method is called when focus is being set on the proxy
        as a result of a user-implemented focus traversal handler.
        This can be reimplemented by subclasses as needed.

        Parameters
        ----------
        reason : Qt.FocusReason
            The reason value for the focus request.

        Returns
        -------
        result : bool
            True if focus was set, False otherwise.

        """
        return False #: TODO: Not yet implemented
        # widget = self.focus_target()
        # if not widget.focusPolicy & Qt.TabFocus:
        #     return False
        # if not widget.isEnabled():
        #     return False
        # if not widget.isVisibleTo(widget.window()):
        #     return False
        # widget.setFocus(reason)
        # return False

    def focus_target(self):
        """ Return the current focus target for a focus request.

        This can be reimplemented by subclasses as needed. The default
        implementation of this method returns the current proxy widget.

        """
        return self.widget

    def hook_focus_traversal(self):
        """ Install the hooks for focus traversal.

        This method may be overridden by subclasses as needed.

        """
        return #: TODO: Not implemented
        #self.widget.focusNextPrevChild = self.focusNextPrevChild

    def unhook_focus_traversal(self):
        """ Remove the hooks for the next/prev child focusing.

        This method may be overridden by subclasses as needed.

        """
        return #: TODO: Not implemented
        #del self.widget.focusNextPrevChild

    def hook_focus_events(self):
        """ Install the hooks for focus events.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        return #: TODO: Not implemented
        #widget.focusInEvent = self.focusInEvent
        #widget.focusOutEvent = self.focusOutEvent

    def unhook_focus_events(self):
        """ Remove the hooks for the focus events.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        return #: TODO: Not implemented
        #del widget.focusInEvent
        #del widget.focusOutEvent

    def focusNextPrevChild(self, next_child):
        """ The default 'focusNextPrevChild' implementation.

        """
        fd = focus_registry.focused_declaration()
        if next_child:
            child = self.declaration.next_focus_child(fd)
            reason = 'tab'#Qt.TabFocusReason
        else:
            child = self.declaration.previous_focus_child(fd)
            reason = 'backtab'#Qt.BacktabFocusReason
        if child is not None and child.proxy_is_active:
            return child.proxy.tab_focus_request(reason)
        widget = self.widget
        return type(widget).focusNextPrevChild(widget, next_child)

    def focusInEvent(self, event):
        """ The default 'focusInEvent' implementation.

        """
        widget = self.widget
        type(widget).focusInEvent(widget, event)
        self.declaration.focus_gained()

    def focusOutEvent(self, event):
        """ The default 'focusOutEvent' implementation.

        """
        widget = self.widget
        type(widget).focusOutEvent(widget, event)
        self.declaration.focus_lost()

    def hook_drag(self):
        """ Install the hooks for drag operations.

        """
        widget = self.widget
        return #: TODO: Not implemented
        # widget.mousePressEvent = self.mousePressEvent
        # widget.mouseMoveEvent = self.mouseMoveEvent
        # widget.mouseReleaseEvent = self.mouseReleaseEvent

    def unhook_drag(self):
        """ Remove the hooks for drag operations.

        """
        widget = self.widget
        return #: TODO: Not implemented
        #
        # del widget.mousePressEvent
        # del widget.mouseMoveEvent
        # del widget.mouseReleaseEvent

    def mousePressEvent(self, event):
        """ Handle the mouse press event for a drag operation.

        """
        return #: TODO: Not implemented
        # if event.button() == Qt.LeftButton:
        #     self._drag_origin = event.pos()
        # widget = self.widget
        # type(widget).mousePressEvent(widget, event)

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for a drag operation.

        """
        return #: TODO: Not implemented
        # if event.buttons() & Qt.LeftButton and self._drag_origin is not None:
        #     dist = (event.pos() - self._drag_origin).manhattanLength()
        #     if dist >= QApplication.startDragDistance():
        #         self.do_drag()
        #         self._drag_origin = None
        #         return
        # widget = self.widget
        # type(widget).mouseMoveEvent(widget, event)

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the drag operation.

        """
        return #: TODO: Not implemented
        # if event.button() == Qt.LeftButton:
        #     self._drag_origin = None
        # widget = self.widget
        # type(widget).mouseReleaseEvent(widget, event)

    def hook_drop(self):
        """ Install hooks for drop operations.

        """
        widget = self.widget
        return #: TODO: Not implemented
        widget.setAcceptDrops(True)
        # widget.dragEnterEvent = self.dragEnterEvent
        # widget.dragMoveEvent = self.dragMoveEvent
        # widget.dragLeaveEvent = self.dragLeaveEvent
        # widget.dropEvent = self.dropEvent

    def unhook_drop(self):
        """ Remove hooks for drop operations.

        """
        widget = self.widget
        return #: TODO: Not implemented
        widget.setAcceptDrops(False)
        # del widget.dragEnterEvent
        # del widget.dragMoveEvent
        # del widget.dragLeaveEvent
        # del widget.dropEvent

    def do_drag(self):
        """ Perform the drag operation for the widget.

        """
        drag_data = self.declaration.drag_start()
        if drag_data is None:
            return
        # widget = self.widget
        # qdrag = QDrag(widget)
        # qdrag.setMimeData(drag_data.mime_data.q_data())
        # if drag_data.image is not None:
        #     qimg = get_cached_qimage(drag_data.image)
        #     qdrag.setPixmap(QPixmap.fromImage(qimg))
        # else:
        #     qdrag.setPixmap(QPixmap.grabWidget(widget))
        # default = Qt.DropAction(drag_data.default_drop_action)
        # supported = Qt.DropActions(drag_data.supported_actions)
        # qresult = qdrag.exec_(supported, default)
        qresult = 0
        self.declaration.drag_end(drag_data, DropAction(int(qresult)))

    def dragEnterEvent(self, event):
        """ Handle the drag enter event for the widget.

        """
        self.declaration.drag_enter(event)

    def dragMoveEvent(self, event):
        """ Handle the drag move event for the widget.

        """
        self.declaration.drag_move(event)

    def dragLeaveEvent(self, event):
        """ Handle the drag leave event for the widget.

        """
        self.declaration.drag_leave()

    def dropEvent(self, event):
        """ Handle the drop event for the widget.

        """
        self.declaration.drop(event)

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def get_action(self, create=False):
        """ Get the shared widget action for this widget.

        This API is used to support widgets in tool bars and menus.

        Parameters
        ----------
        create : bool, optional
            Whether to create the action if it doesn't already exist.
            The default is False.

        Returns
        -------
        result : QWidgetAction or None
            The cached widget action or None, depending on arguments.

        """
        return None
        action = self._widget_action
        # if action is None and create:
        #     action = self._widget_action = QWidgetAction(None)
        #     action.setDefaultWidget(self.widget)
        # return action

    #--------------------------------------------------------------------------
    # ProxyWidget API
    #--------------------------------------------------------------------------
    def set_minimum_size(self, min_size):
        """ Sets the minimum size of the widget.

        """
        # QWidget uses (0, 0) as the minimum size.
        if -1 in min_size:
            min_size = (0, 0)
        w,h = min_size
        self.widget.setMinimumWidth(w)
        self.widget.setMinimumHeight(h)

    def set_maximum_size(self, max_size):
        """ Sets the maximum size of the widget.

        """
        # QWidget uses 16777215 as the max size
        if -1 in max_size:
            max_size = (16777215, 16777215)
        w, h = max_size
        self.widget.setMaximumWidth(w)
        self.widget.setMaximumHeight(h)

    def set_enabled(self, enabled):
        """ Set the enabled state of the widget.

        """
        self.widget.setEnabled(enabled)
        #action = self._widget_action
        #if action is not None:
        #    action.setEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visibility of the widget.

        """
        self.widget.setVisibility(0 if visible else 2)
        #action = self._widget_action
        #if action is not None:
        #    action.setVisible(visible)

    def set_background(self, background):
        """ Set the background color of the widget.

        """
        return # TODO: Not implemented
        # widget = self.widget
        # role = widget.backgroundRole()
        # if background is not None:
        #     qcolor = get_cached_qcolor(background)
        #     widget.setAutoFillBackground(True)
        # else:
        #     app_palette = QApplication.instance().palette(widget)
        #     qcolor = app_palette.color(role)
        #     widget.setAutoFillBackground(False)
        # palette = widget.palette()
        # palette.setColor(role, qcolor)
        # widget.setPalette(palette)

    def set_foreground(self, foreground):
        """ Set the foreground color of the widget.

        """
        return # TODO: Not implemented
        # widget = self.widget
        # role = widget.foregroundRole()
        # if foreground is not None:
        #     qcolor = get_cached_qcolor(foreground)
        # else:
        #     app_palette = QApplication.instance().palette(widget)
        #     qcolor = app_palette.color(role)
        # palette = widget.palette()
        # palette.setColor(role, qcolor)
        # widget.setPalette(palette)

    def set_font(self, font):
        """ Set the font of the widget.

        """
        return # Not implemented
        #if font is not None:
        #    self.widget.setFont(get_cached_qfont(font))
        #else:
        #    self.widget.setFont(QFont())

    def set_tool_tip(self, tool_tip):
        """ Set the tool tip for the widget.

        """
        self.widget.setToolTipText(tool_tip)

    def set_status_tip(self, status_tip):
        """ Set the status tip for the widget.

        """
        return # Not implemented on android
        #self.widget.setStatusTip(status_tip)

    def ensure_visible(self):
        """ Ensure the widget is visible.

        """
        # 0 - visible, 1 - invisible, 2 - gone
        self.widget.setVisibility(0)
        #action = self._widget_action
        #if action is not None:
        #    action.setVisible(True)

    def ensure_hidden(self):
        """ Ensure the widget is hidden.

        """
        # 0 - visible, 1 - invisible, 2 - gone
        self.widget.setVisible(2)
        #action = self._widget_action
        #if action is not None:
        #    action.setVisible(False)

    def restyle(self):
        """ Restyle the widget with the current style data.

        """
        self.refresh_style_sheet()

    def set_focus(self):
        """ Set the keyboard input focus to this widget.

        """
        self.focus_target().requestFocus()

    def clear_focus(self):
        """ Clear the keyboard input focus from this widget.

        """
        self.focus_target().clearFocus()

    def has_focus(self):
        """ Test whether this widget has input focus.

        """
        return self.focus_target().hasFocus()

    def focus_next_child(self):
        """ Give focus to the next widget in the focus chain.

        """
        return # TODO: Not yet implemeneted
        self.focus_target().focusNextChild()

    def focus_previous_child(self):
        """ Give focus to the previous widget in the focus chain.

        """
        return # TODO: Not yet implemeneted
        self.focus_target().focusPreviousChild()