from math import floor, cos, sin

from manim import *
import config as conf
import os


class StarAnimation(Scene):
    def construct(self):
        # Setup the outer and inner circles
        points, distance_between_points = conf.star_label()
        outer_circle = Circle(radius=3, color=GRAY)

        inner_circle = Circle(radius=outer_circle.radius * distance_between_points / points, color=WHITE)
        inner_circle_starting_point = [outer_circle.radius - inner_circle.radius, 0, 0]
        inner_circle.move_to(inner_circle_starting_point)
        inner_circle_bound = inner_circle.get_center() + [inner_circle.radius, 0, 0]
        inner_circle_radius_line = DashedLine(inner_circle.get_center(), inner_circle_bound)
        inner_circle_dot = Dot(inner_circle_bound, color=RED)

        self.play(Create(outer_circle), Create(inner_circle), Create(inner_circle_radius_line),
                  Create(inner_circle_dot))

        self.wait()

        # Trace out the star path
        inner_circle_group = VGroup(inner_circle, inner_circle_radius_line, inner_circle_dot)
        star_path = TracedPath(inner_circle_dot.get_center, stroke_width=2, stroke_color=RED)

        star_path_duration = conf.star_path_duration()

        def Rolling(roll_duration, m, dt):
            m.rotate(dt * TAU / roll_duration, about_point=outer_circle.get_center()) \
                .rotate(-dt * TAU / roll_duration * points / distance_between_points, about_point=m[0].get_center())

        self.add(star_path, inner_circle_group)

        def StarPathRolling(m, dt):
            Rolling(star_path_duration / distance_between_points, m, dt)

        inner_circle_group.add_updater(StarPathRolling)
        self.wait(star_path_duration + 1 / config.frame_rate)
        inner_circle_group.remove_updater(StarPathRolling)
        star_path.clear_updaters()

        self.wait()

        # Animate how the green polygons are constructed
        self.play(inner_circle_dot.animate.set_color(GREEN))

        green_dots = []
        green_dots_group = VGroup()

        self.wait()
        inner_circle_dot.set_opacity(0)
        green_polygon_duration = conf.green_polygon_duration()

        def GreenPolygonRolling(m, dt):
            Rolling(green_polygon_duration * points / distance_between_points, m, dt)

        def GreenPolygonUnrolling(m, dt):
            Rolling(-green_polygon_duration * points / distance_between_points, m, dt)

        inner_circle_group.add_updater(GreenPolygonRolling)
        inner_circle_group.suspend_updating()
        green_dots.append(inner_circle_dot.copy().set_opacity(1))
        green_dots_group += green_dots[-1]
        self.add(green_dots_group)
        inner_circle_group += green_dots_group

        for j in range(1, distance_between_points):
            inner_circle_group.resume_updating()
            self.wait(green_polygon_duration / distance_between_points + 1 / config.frame_rate)
            inner_circle_group.suspend_updating()
            green_dots.append(inner_circle_dot.copy().set_opacity(1).rotate(TAU * j / distance_between_points,
                                                                            about_point=inner_circle.get_center()))
            green_dots_group += green_dots[-1]

        green_polygon = Polygon(*[dot.get_center() for dot in green_dots], color=GREEN)
        green_dots_group += green_polygon
        self.play(Create(green_polygon))
        inner_circle_group.remove_updater(GreenPolygonRolling)
        inner_circle_group.resume_updating()
        self.wait()

        inner_circle_group.add_updater(GreenPolygonUnrolling)
        self.wait(
            green_polygon_duration * (distance_between_points - 1) / distance_between_points + 1 / config.frame_rate)
        inner_circle_group.remove_updater(GreenPolygonUnrolling)

        inner_circle_group -= green_dots_group
        inner_circle_dot.set_opacity(1)
        self.play(FadeOut(green_dots_group))

        # Animate how the blue polygons are constructed
        self.play(inner_circle_dot.animate.set_color(BLUE))

        blue_dots = []
        blue_dots_group = VGroup()

        self.wait()
        inner_circle_dot.set_opacity(0)
        blue_polygon_duration = conf.blue_polygon_duration()

        def BluePolygonRolling(m, dt):
            Rolling(blue_polygon_duration / distance_between_points, m, dt)

        inner_circle_group.add_updater(BluePolygonRolling)
        inner_circle_group.suspend_updating()
        blue_dots.append(inner_circle_dot.copy().set_opacity(1))
        blue_dots_group += blue_dots[-1]
        self.add(blue_dots_group)

        for j in range(1, points - distance_between_points):
            inner_circle_group.resume_updating()
            self.wait(blue_polygon_duration / (points - distance_between_points) + 1 / config.frame_rate)
            inner_circle_group.suspend_updating()
            blue_dots.append(inner_circle_dot.copy().set_opacity(1))
            blue_dots_group += blue_dots[-1]

        blue_polygon = Polygon(*[dot.get_center() for dot in blue_dots], color=BLUE)
        blue_dots_group += blue_polygon
        self.play(Create(blue_polygon))
        inner_circle_group.remove_updater(BluePolygonRolling)

        # Animate all the polygons moving along the star path
        self.wait()
        self.play(FadeOut(inner_circle_group), FadeOut(blue_dots_group))

        class MovePolygonAlongStarPath(MoveAlongPath):
            def __init__(
                    self,
                    mobject: "Mobject",
                    start_dot: "Dot",
                    start: float,
                    end: float,
                    dir: float = 1,
                    suspend_mobject_updating: Optional[bool] = False,
                    **kwargs
            ) -> None:
                self.start_dot = start_dot
                self.start = start
                self.end = end
                self.dir = dir
                super().__init__(
                    mobject, star_path, suspend_mobject_updating=suspend_mobject_updating, **kwargs
                )

            def interpolate_mobject(self, alpha: float) -> None:
                r = self.start + self.rate_func(alpha) * (self.end - self.start)
                r -= floor(r)

                self.mobject.become(self.starting_mobject)
                self.mobject.rotate(self.rate_func(alpha) * self.dir * TAU * (self.end - self.start))
                point = self.star_path_point(r) - self.start_dot.get_center() + self.mobject.get_center()
                self.mobject.move_to(point)

            def star_path_point(self, t):
                R, r = outer_circle.radius, inner_circle.radius
                theta = t * TAU * distance_between_points
                return [(R - r) * cos(theta) + r * cos((R - r) / r * theta),
                        (R - r) * sin(theta) - r * sin((R - r) / r * theta), 0]

        self.wait()

        all_green_dots = [
            [green_dot.copy().move_to(
                blue_dot.get_center() + green_dot.get_center() - green_dots[0].get_center()
            ) for green_dot in green_dots]
            for blue_dot in blue_dots
        ]
        all_green_polygon_groups = [
            VGroup(Polygon(*map(Dot.get_center, green_polygon_dots), color=GREEN), *green_polygon_dots)
            for green_polygon_dots in all_green_dots
        ]

        all_blue_dots = [
            [blue_dot.copy().move_to(
                green_dot.get_center() + blue_dot.get_center() - blue_dots[0].get_center()
            ) for blue_dot in blue_dots]
            for green_dot in green_dots
        ]
        all_blue_polygon_groups = [
            VGroup(Polygon(*map(Dot.get_center, blue_polygon_dots), color=BLUE), *blue_polygon_dots)
            for blue_polygon_dots in all_blue_dots
        ]

        animation_duration, animation_repeats = conf.animation_duration(), conf.animation_repeats()
        self.play(*[Create(polygon_group) for polygon_group in all_green_polygon_groups])
        self.wait()
        self.play(
            *[MovePolygonAlongStarPath(all_green_polygon_groups[i], all_green_dots[i][0],
                                       i / (points - distance_between_points),
                                       animation_repeats + i / (points - distance_between_points),
                                       dir=distance_between_points - points, rate_func=linear,
                                       run_time=animation_duration * animation_repeats) for i in
              range(len(all_green_polygon_groups))]
        )
        self.wait()
        self.play(*[FadeOut(polygon_group) for polygon_group in all_green_polygon_groups],
                  *[Create(polygon_group) for polygon_group in all_blue_polygon_groups])
        self.wait()
        self.play(
            *[MovePolygonAlongStarPath(all_blue_polygon_groups[i], all_blue_dots[i][0],
                                       (distance_between_points - i) / distance_between_points,
                                       animation_repeats + (distance_between_points - i) / distance_between_points,
                                       dir=distance_between_points, rate_func=linear,
                                       run_time=animation_duration * animation_repeats) for i in
              range(len(all_blue_polygon_groups))]
        )
        self.wait()
        for green_polygon_dots in all_green_dots:
            for green_dot in green_polygon_dots:
                green_dot.set_opacity(0)
        self.play(
            *[FadeIn(polygon_group) for polygon_group in all_green_polygon_groups],
            *[blue_dot.animate.set_color(YELLOW) for blue_polygon_dots in all_blue_dots for blue_dot in blue_polygon_dots]
        )
        self.wait()
        self.play(
            *[MovePolygonAlongStarPath(all_green_polygon_groups[i], all_green_dots[i][0],
                                       i / (points - distance_between_points),
                                       animation_repeats + i / (points - distance_between_points),
                                       dir=distance_between_points - points, rate_func=linear,
                                       run_time=animation_duration * animation_repeats) for i in
              range(len(all_green_polygon_groups))],
            *[MovePolygonAlongStarPath(all_blue_polygon_groups[i], all_blue_dots[i][0],
                                       (distance_between_points - i) / distance_between_points,
                                       animation_repeats + (distance_between_points - i) / distance_between_points,
                                       dir=distance_between_points, rate_func=linear,
                                       run_time=animation_duration * animation_repeats) for i in
              range(len(all_blue_polygon_groups))]
        )
        self.wait()


if __name__ == '__main__':
    os.system('manim -pqh animation.py StarAnimation')
