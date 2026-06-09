# -*- coding: utf-8 -*-
from __future__ import annotations

from support import TestCase, TestContext, assert_equal, assert_true, chromium, html, local_server


def run(ctx: TestContext) -> None:
    routes = {
        "/object-host": lambda _req: html("""
            <body>
              <iframe id='f' src='/object-child'></iframe>
              <object id='obj' data='/object-child' type='text/html'></object>
            </body>
        """, title="object host"),
        "/object-child": lambda _req: html("<body><p id='child'>child</p></body>", title="object child"),
    }
    with local_server(routes) as base, chromium(ctx) as browser:
        from DrissionPage.items import ChromiumFrame

        tab = browser.latest_tab
        nav = tab.get(base + "/object-host")
        assert_true(nav is True or bool(nav) is True, "object host page should load", nav=nav)
        assert_true(tab.wait.eles_loaded(("tag:iframe", "tag:object"), timeout=ctx.timeout), "iframe and object elements should load")

        obj = tab.ele("tag:object", timeout=ctx.timeout)
        assert_true(isinstance(obj, ChromiumFrame), "tag:object should be converted to ChromiumFrame", obj=obj)
        assert_equal(obj.attr("id"), "obj", "object frame id mismatch")

        frames = list(tab.get_frames(timeout=ctx.timeout))
        frame_ids = {frame.attr("id") for frame in frames}
        assert_true({"f", "obj"} <= frame_ids, "get_frames() default should include iframe and object", frame_ids=frame_ids)
        assert_true(all(isinstance(frame, ChromiumFrame) for frame in frames), "get_frames() should return ChromiumFrame objects", frames=frames)

        iframe_only = list(tab.get_frames('xpath://*[name()="iframe" or name()="frame"]', timeout=ctx.timeout))
        assert_equal([frame.attr("id") for frame in iframe_only], ["f"], "explicit iframe/frame locator should remain narrowed")

        object_only = list(tab.get_frames("tag:object", timeout=ctx.timeout))
        assert_equal([frame.attr("id") for frame in object_only], ["obj"], "explicit object locator should find object frame")


TEST_CASE = TestCase(
    name="object_frame_default",
    title="get_frames() default includes object frame-like elements",
    requires_browser=True,
    features=("object_frame_default",),
    run=run,
)
