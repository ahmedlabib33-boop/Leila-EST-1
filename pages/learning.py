import math
import re

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from ai.course_generator.english_course_generator import generate_english_course
from ai.course_generator.math_course_generator import generate_math_course
from loaders.learning_loader import (
    load_english_content,
    load_english_questions,
    load_math_content,
    load_math_questions,
)


def _text(value):
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return str(value).strip()


def _parts(value):
    return [part.strip() for part in _text(value).split("|") if part.strip()]


def _show_parts(value, renderer=st.info):
    for part in _parts(value):
        renderer(part)


def _to_math_token(value):
    token = _text(value)
    token = token.replace("×", r"\times ")
    token = token.replace("÷", r"\div ")
    token = token.replace("−", "-")
    token = token.replace("√", r"\sqrt")
    token = re.sub(r"([A-Za-z])(\d+)", r"\1_{\2}", token)
    token = token.replace("²", "^2").replace("³", "^3")
    token = token.replace("π", r"\pi")
    token = token.replace("θ", r"\theta")
    return token


def _split_top_level(value, separators):
    parts = []
    operators = []
    start = 0
    depth = 0
    for index, char in enumerate(value):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and char in separators:
            parts.append(value[start:index])
            operators.append(char)
            start = index + 1
    parts.append(value[start:])
    return parts, operators


def _strip_outer_parentheses(value):
    value = _text(value)
    if not (value.startswith("(") and value.endswith(")")):
        return value

    depth = 0
    for index, char in enumerate(value):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0 and index != len(value) - 1:
                return value
    return value[1:-1]


def _format_math_expression(value):
    value = _text(value)
    if not value:
        return ""

    parts, operators = _split_top_level(value, "=+-×÷")
    if operators:
        rendered = [_format_math_expression(parts[0])]
        for operator, part in zip(operators, parts[1:]):
            operator_text = {
                "×": r" \times ",
                "÷": r" \div ",
            }.get(operator, f" {operator} ")
            rendered.append(operator_text)
            rendered.append(_format_math_expression(part))
        return "".join(rendered)

    numerator_denominator, slash_ops = _split_top_level(value, "/")
    if slash_ops and len(numerator_denominator) == 2:
        numerator = _format_math_expression(_strip_outer_parentheses(numerator_denominator[0]))
        denominator = _format_math_expression(_strip_outer_parentheses(numerator_denominator[1]))
        return rf"\frac{{{numerator}}}{{{denominator}}}"

    return _to_math_token(value)


def _show_formula(value):
    formula = _text(value)
    if not formula:
        return

    formula_like = any(char in formula for char in "/=+-×÷√πθ²³^")
    if formula_like:
        st.latex(_format_math_expression(formula))
    else:
        st.info(formula)


def _difficulty_score(value):
    scores = {"Easy": 1, "Medium": 2, "Hard": 3}
    return scores.get(_text(value), 0)


def _show_math_topic_visuals(df, topic_df):
    st.markdown("### Math Topic Visualizations")

    topic_lessons = topic_df.drop_duplicates("lesson_title")
    lesson_count = topic_lessons["lesson_title"].nunique()
    formula_count = topic_lessons["formula"].apply(lambda value: bool(_text(value))).sum()
    average_difficulty = topic_lessons["difficulty"].apply(_difficulty_score).mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Lessons In Topic", lesson_count)
    col2.metric("Lessons With Formulas", int(formula_count))
    col3.metric("Average Difficulty", f"{average_difficulty:.1f} / 3")

    col1, col2 = st.columns(2)

    with col1:
        st.write("##### Lessons Per Math Domain")
        domain_counts = (
            df.groupby("domain")["lesson_title"]
            .nunique()
            .sort_values(ascending=False)
        )
        st.bar_chart(domain_counts)

    with col2:
        st.write("##### Difficulty In Selected Topic")
        difficulty_order = ["Easy", "Medium", "Hard"]
        difficulty_counts = (
            topic_lessons["difficulty"]
            .value_counts()
            .reindex(difficulty_order, fill_value=0)
        )
        st.bar_chart(difficulty_counts)

    st.write("##### Selected Topic Lesson Map")
    lesson_map = topic_lessons[["lesson_title", "difficulty", "formula"]].copy()
    lesson_map["has_example"] = topic_lessons["example"].apply(
        lambda value: "Yes" if _text(value) else "No"
    )
    lesson_map = lesson_map.rename(
        columns={
            "lesson_title": "Lesson",
            "difficulty": "Difficulty",
            "formula": "Formula",
            "has_example": "Example",
        }
    )
    st.dataframe(lesson_map, use_container_width=True, hide_index=True)


def _sample_graph_data(row):
    title = _text(row.get("lesson_title")).lower()
    formula = _text(row.get("formula")).lower()
    combined = f"{title} {formula}"
    x_values = list(range(-5, 6))

    if any(keyword in combined for keyword in ["slope", "linear", "y=mx+b", "ax+b"]):
        return (
            "Equation Plot: y = 2x + 1",
            pd.DataFrame({"x": x_values, "y": [2 * x + 1 for x in x_values]}),
            "line",
        )

    if any(keyword in combined for keyword in ["quadratic", "vertex", "ax2", "x2", "x^2"]):
        return (
            "Equation Plot: y = x^2 - 2x - 3",
            pd.DataFrame({"x": x_values, "y": [x**2 - 2 * x - 3 for x in x_values]}),
            "line",
        )

    if any(keyword in combined for keyword in ["absolute value", "|x|"]):
        return (
            "Equation Plot: y = |x|",
            pd.DataFrame({"x": x_values, "y": [abs(x) for x in x_values]}),
            "line",
        )

    if any(keyword in combined for keyword in ["exponential", "growth", "a(b)^x"]):
        return (
            "Equation Plot: y = 2^x",
            pd.DataFrame({"x": list(range(0, 8)), "y": [2**x for x in range(0, 8)]}),
            "line",
        )

    if "circle" in combined:
        points = []
        radius = 5
        for step in range(0, 37):
            angle = step * 10
            radians = angle * math.pi / 180
            points.append(
                {
                    "angle": angle,
                    "x": radius * math.cos(radians),
                    "y": radius * math.sin(radians),
                }
            )
        return "Equation Plot: x^2 + y^2 = 25", pd.DataFrame(points), "circle"

    return None, None, None


def _show_equation_plot(row):
    graph_title, graph_df, graph_type = _sample_graph_data(row)
    if graph_df is None:
        return False

    st.write(f"##### {graph_title}")
    if graph_type == "circle":
        st.vega_lite_chart(
            graph_df,
            {
                "mark": {"type": "line", "point": True},
                "encoding": {
                    "x": {"field": "x", "type": "quantitative"},
                    "y": {"field": "y", "type": "quantitative"},
                    "tooltip": [
                        {"field": "x", "type": "quantitative"},
                        {"field": "y", "type": "quantitative"},
                    ],
                },
            },
            use_container_width=True,
        )
    else:
        st.line_chart(graph_df.set_index("x"))

    return True


def _is_triangle_area_lesson(row):
    combined = f"{_text(row.get('lesson_title'))} {_text(row.get('formula'))}".lower()
    return "triangle" in combined and any(keyword in combined for keyword in ["area", "surface"])


def _show_geometry_visual(title, svg_body, explanation):
    st.write(f"##### {title}")
    components.html(
        f"""
<div style="width:100%; display:flex; justify-content:center;">
  <svg viewBox="0 0 620 330" width="100%" height="330" role="img" aria-label="{title}" style="max-width:760px;">
    <rect x="1" y="1" width="618" height="328" rx="18" fill="#f8fafc" stroke="#d7dee8"/>
    <style>
      .math-label {{ font-family: Arial, sans-serif; fill: #0f172a; font-size: 24px; }}
      .math-blue {{ font-family: Arial, sans-serif; fill: #1d4ed8; font-size: 24px; }}
      .math-red {{ font-family: Arial, sans-serif; fill: #dc2626; font-size: 22px; }}
      .math-small {{ font-family: Arial, sans-serif; fill: #334155; font-size: 20px; }}
    </style>
    {svg_body}
  </svg>
</div>
        """,
        height=350,
    )
    st.info(explanation)
    return True


def _show_geometry_formula_visual(row):
    title = _text(row.get("lesson_title"))
    formula = _text(row.get("formula"))
    combined = f"{title} {formula}".lower()

    if "rectangle area" in combined:
        return _show_geometry_visual(
            "Rectangle Area Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">Area = length x width</text>
  <rect x="150" y="88" width="320" height="170" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <text x="310" y="292" text-anchor="middle" class="math-small">length = l</text>
  <text x="485" y="178" class="math-red">width = w</text>
  <text x="310" y="178" text-anchor="middle" class="math-blue">Rectangle</text>
            """,
            "The area counts how many square units cover the inside of the rectangle. Multiply the length by the width, so A = l x w.",
        )

    if "rectangle perimeter" in combined:
        return _show_geometry_visual(
            "Rectangle Perimeter Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">Perimeter = 2(length + width)</text>
  <rect x="150" y="88" width="320" height="170" fill="#dbeafe" stroke="#2563eb" stroke-width="5"/>
  <path d="M140 78 H480 V268 H140 Z" fill="none" stroke="#dc2626" stroke-width="3" stroke-dasharray="10 8"/>
  <text x="310" y="292" text-anchor="middle" class="math-small">two lengths + two widths</text>
  <text x="310" y="178" text-anchor="middle" class="math-blue">Around the outside</text>
            """,
            "The perimeter is the distance around the rectangle. Add length and width, then double it because there are two equal lengths and two equal widths.",
        )

    if _is_triangle_area_lesson(row):
        return _show_geometry_visual(
            "Triangle Area Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">Area = 1/2 x base x height</text>
  <polygon points="110,260 510,260 235,70" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <line x1="235" y1="70" x2="235" y2="260" stroke="#dc2626" stroke-width="4" stroke-dasharray="8 8"/>
  <path d="M235 260 L265 260 L265 230" fill="none" stroke="#dc2626" stroke-width="3"/>
  <text x="310" y="298" text-anchor="middle" class="math-small">base = b</text>
  <text x="255" y="165" class="math-red">height = h</text>
  <text x="340" y="120" class="math-blue">Triangle</text>
            """,
            "The base is the bottom side of the triangle. The height is the straight perpendicular distance from the top point down to the base. A triangle is half of a matching rectangle, so its area is 1/2 x base x height.",
        )

    if "triangle angle sum" in combined:
        return _show_geometry_visual(
            "Triangle Angle Sum Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">A + B + C = 180°</text>
  <polygon points="115,260 505,260 300,75" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <text x="130" y="245" class="math-red">A</text>
  <text x="480" y="245" class="math-red">B</text>
  <text x="292" y="105" class="math-red">C</text>
  <text x="310" y="300" text-anchor="middle" class="math-small">all inside angles add to 180°</text>
            """,
            "Every triangle has three inside angles. No matter the shape of the triangle, those three angles always add up to 180 degrees.",
        )

    if "right triangle" in combined or "a²+b²=c²" in combined:
        return _show_geometry_visual(
            "Right Triangle Rule Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">a² + b² = c²</text>
  <polygon points="160,260 460,260 160,95" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <path d="M160 260 L190 260 L190 230" fill="none" stroke="#dc2626" stroke-width="3"/>
  <text x="300" y="292" text-anchor="middle" class="math-small">leg = a</text>
  <text x="118" y="180" class="math-small">leg = b</text>
  <text x="320" y="160" class="math-red">hypotenuse = c</text>
            """,
            "In a right triangle, the two shorter sides are the legs and the longest side is the hypotenuse. Square both legs and add them to get the square of the hypotenuse.",
        )

    if "circle equation" in combined:
        return _show_geometry_visual(
            "Circle Equation Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">(x - h)² + (y - k)² = r²</text>
  <line x1="80" y1="175" x2="540" y2="175" stroke="#94a3b8" stroke-width="2"/>
  <line x1="310" y1="65" x2="310" y2="285" stroke="#94a3b8" stroke-width="2"/>
  <circle cx="310" cy="175" r="95" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <circle cx="310" cy="175" r="5" fill="#dc2626"/>
  <line x1="310" y1="175" x2="405" y2="175" stroke="#dc2626" stroke-width="4"/>
  <text x="322" y="166" class="math-red">center (h,k)</text>
  <text x="350" y="205" class="math-red">r</text>
            """,
            "A circle equation describes all points that are the same distance from the center. The center is (h,k), and r is the radius from the center to the circle.",
        )

    if "circle area" in combined:
        return _show_geometry_visual(
            "Circle Area Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">Area = πr²</text>
  <circle cx="310" cy="175" r="105" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <line x1="310" y1="175" x2="415" y2="175" stroke="#dc2626" stroke-width="4"/>
  <circle cx="310" cy="175" r="5" fill="#dc2626"/>
  <text x="350" y="205" class="math-red">radius = r</text>
  <text x="310" y="300" text-anchor="middle" class="math-small">inside space of the circle</text>
            """,
            "Circle area measures the inside surface of the circle. Use the radius, square it, then multiply by pi, so A = πr².",
        )

    if "circumference" in combined:
        return _show_geometry_visual(
            "Circumference Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">Circumference = 2πr</text>
  <circle cx="310" cy="175" r="105" fill="#dbeafe" stroke="#2563eb" stroke-width="5"/>
  <circle cx="310" cy="175" r="5" fill="#dc2626"/>
  <line x1="310" y1="175" x2="415" y2="175" stroke="#dc2626" stroke-width="4"/>
  <text x="355" y="205" class="math-red">r</text>
  <text x="310" y="300" text-anchor="middle" class="math-small">distance around the circle</text>
            """,
            "Circumference is the distance around the outside of the circle. It is the circle version of perimeter, and the formula is 2πr.",
        )

    if "rectangular prism volume" in combined:
        return _show_geometry_visual(
            "Rectangular Prism Volume Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">Volume = length x width x height</text>
  <polygon points="175,120 430,120 490,175 235,175" fill="#eff6ff" stroke="#2563eb" stroke-width="3"/>
  <polygon points="235,175 490,175 490,275 235,275" fill="#dbeafe" stroke="#2563eb" stroke-width="3"/>
  <polygon points="175,120 235,175 235,275 175,220" fill="#bfdbfe" stroke="#2563eb" stroke-width="3"/>
  <text x="360" y="302" text-anchor="middle" class="math-small">l x w x h</text>
  <text x="500" y="230" class="math-red">height</text>
            """,
            "Volume measures how much space is inside the rectangular prism. Multiply length, width, and height, so V = lwh.",
        )

    if "cube volume" in combined:
        return _show_geometry_visual(
            "Cube Volume Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">Volume = s³</text>
  <polygon points="215,110 405,110 455,160 265,160" fill="#eff6ff" stroke="#2563eb" stroke-width="3"/>
  <polygon points="265,160 455,160 455,275 265,275" fill="#dbeafe" stroke="#2563eb" stroke-width="3"/>
  <polygon points="215,110 265,160 265,275 215,225" fill="#bfdbfe" stroke="#2563eb" stroke-width="3"/>
  <text x="360" y="302" text-anchor="middle" class="math-small">side = s</text>
  <text x="300" y="205" class="math-blue">same side length</text>
            """,
            "A cube has the same side length in every direction. Multiply side x side x side, which is written as s³.",
        )

    if "sine ratio" in combined or "cosine ratio" in combined or "tangent ratio" in combined:
        ratio_label = "sin = opposite / hypotenuse"
        if "cosine" in combined:
            ratio_label = "cos = adjacent / hypotenuse"
        if "tangent" in combined:
            ratio_label = "tan = opposite / adjacent"
        return _show_geometry_visual(
            "Right Triangle Ratio Visualization",
            f"""
  <text x="310" y="44" text-anchor="middle" class="math-label">{ratio_label}</text>
  <polygon points="165,260 465,260 165,95" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <path d="M165 260 L195 260 L195 230" fill="none" stroke="#dc2626" stroke-width="3"/>
  <text x="305" y="292" text-anchor="middle" class="math-small">adjacent</text>
  <text x="95" y="180" class="math-red">opposite</text>
  <text x="310" y="155" class="math-blue">hypotenuse</text>
  <text x="205" y="245" class="math-red">θ</text>
            """,
            "Sine, cosine, and tangent compare two sides of a right triangle from one chosen angle. Opposite is across from the angle, adjacent touches the angle, and hypotenuse is the longest side.",
        )

    if "distance formula" in combined:
        return _show_geometry_visual(
            "Distance Formula Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">distance = √((x₂-x₁)² + (y₂-y₁)²)</text>
  <line x1="105" y1="255" x2="535" y2="255" stroke="#94a3b8" stroke-width="2"/>
  <line x1="105" y1="60" x2="105" y2="255" stroke="#94a3b8" stroke-width="2"/>
  <circle cx="190" cy="220" r="7" fill="#dc2626"/>
  <circle cx="450" cy="105" r="7" fill="#dc2626"/>
  <line x1="190" y1="220" x2="450" y2="105" stroke="#2563eb" stroke-width="4"/>
  <line x1="190" y1="220" x2="450" y2="220" stroke="#dc2626" stroke-width="3" stroke-dasharray="8 8"/>
  <line x1="450" y1="220" x2="450" y2="105" stroke="#dc2626" stroke-width="3" stroke-dasharray="8 8"/>
  <text x="175" y="245" class="math-small">(x₁,y₁)</text>
  <text x="460" y="98" class="math-small">(x₂,y₂)</text>
            """,
            "The distance formula finds the straight-line distance between two points. It uses the horizontal change and vertical change to form a right triangle.",
        )

    if "midpoint" in combined:
        return _show_geometry_visual(
            "Midpoint Formula Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">midpoint = ((x₁+x₂)/2, (y₁+y₂)/2)</text>
  <line x1="105" y1="255" x2="535" y2="255" stroke="#94a3b8" stroke-width="2"/>
  <line x1="105" y1="60" x2="105" y2="255" stroke="#94a3b8" stroke-width="2"/>
  <line x1="170" y1="220" x2="470" y2="100" stroke="#2563eb" stroke-width="4"/>
  <circle cx="170" cy="220" r="7" fill="#dc2626"/>
  <circle cx="470" cy="100" r="7" fill="#dc2626"/>
  <circle cx="320" cy="160" r="9" fill="#16a34a"/>
  <text x="330" y="155" class="math-red">middle point</text>
            """,
            "The midpoint is exactly halfway between two points. Average the x-values and average the y-values to find the center point.",
        )

    if "similar triangle" in combined:
        return _show_geometry_visual(
            "Similar Triangles Ratio Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">side₁ / side₂ = side₃ / side₄</text>
  <polygon points="95,260 275,260 95,125" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <polygon points="345,260 555,260 345,105" fill="#eff6ff" stroke="#2563eb" stroke-width="4"/>
  <text x="178" y="292" text-anchor="middle" class="math-small">small triangle</text>
  <text x="450" y="292" text-anchor="middle" class="math-small">larger matching triangle</text>
  <text x="300" y="175" class="math-red">same shape</text>
            """,
            "Similar triangles have the same shape but different sizes. Matching sides grow by the same scale factor, so their side ratios are equal.",
        )

    if "arc length" in combined:
        return _show_geometry_visual(
            "Arc Length Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">arc length = rθ</text>
  <path d="M210 245 A120 120 0 0 1 410 110" fill="none" stroke="#2563eb" stroke-width="8"/>
  <line x1="310" y1="245" x2="210" y2="245" stroke="#dc2626" stroke-width="4"/>
  <line x1="310" y1="245" x2="410" y2="110" stroke="#dc2626" stroke-width="4"/>
  <circle cx="310" cy="245" r="5" fill="#dc2626"/>
  <text x="245" y="238" class="math-red">r</text>
  <text x="323" y="215" class="math-red">θ</text>
            """,
            "Arc length measures part of the circle's edge. When the angle is in radians, multiply the radius by the central angle: arc length = rθ.",
        )

    if "sector area" in combined:
        return _show_geometry_visual(
            "Sector Area Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">sector area = 1/2 r²θ</text>
  <path d="M310 245 L210 245 A120 120 0 0 1 410 110 Z" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <line x1="310" y1="245" x2="210" y2="245" stroke="#dc2626" stroke-width="4"/>
  <line x1="310" y1="245" x2="410" y2="110" stroke="#dc2626" stroke-width="4"/>
  <text x="250" y="238" class="math-red">r</text>
  <text x="325" y="214" class="math-red">θ</text>
            """,
            "A sector is a slice of a circle. Its area depends on the radius and the central angle in radians, so the formula is 1/2 r²θ.",
        )

    if "diameter relation" in combined or "radius relation" in combined:
        formula_label = "diameter = 2r" if "diameter" in combined else "radius = d/2"
        return _show_geometry_visual(
            "Radius and Diameter Visualization",
            f"""
  <text x="310" y="44" text-anchor="middle" class="math-label">{formula_label}</text>
  <circle cx="310" cy="175" r="105" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <line x1="205" y1="175" x2="415" y2="175" stroke="#dc2626" stroke-width="4"/>
  <line x1="310" y1="175" x2="415" y2="175" stroke="#16a34a" stroke-width="6"/>
  <circle cx="310" cy="175" r="5" fill="#dc2626"/>
  <text x="285" y="165" class="math-red">d</text>
  <text x="355" y="205" class="math-small">r</text>
            """,
            "The diameter goes all the way across the circle through the center. The radius goes from the center to the circle, so the diameter is two radii and the radius is half the diameter.",
        )

    if "complementary identity" in combined:
        return _show_geometry_visual(
            "Complementary Trig Identity Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">sin(x) = cos(90 - x)</text>
  <polygon points="165,260 465,260 165,95" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <path d="M165 260 L195 260 L195 230" fill="none" stroke="#dc2626" stroke-width="3"/>
  <text x="205" y="245" class="math-red">x</text>
  <text x="172" y="128" class="math-red">90 - x</text>
  <text x="305" y="292" text-anchor="middle" class="math-small">the acute angles complete 90 degrees</text>
  <text x="310" y="155" class="math-blue">same triangle sides</text>
            """,
            "In a right triangle, the two acute angles add to 90 degrees. The side opposite angle x is adjacent to angle 90 - x, so sin(x) equals cos(90 - x).",
        )

    if "complementary" in combined or "supplementary" in combined:
        is_comp = "complementary" in combined
        sum_label = "sum = 90°" if is_comp else "sum = 180°"
        angle_path = "M170 255 L420 255 L420 75" if is_comp else "M120 255 H500"
        return _show_geometry_visual(
            "Angle Sum Visualization",
            f"""
  <text x="310" y="44" text-anchor="middle" class="math-label">{sum_label}</text>
  <path d="{angle_path}" fill="none" stroke="#2563eb" stroke-width="5"/>
  <path d="M420 255 A95 95 0 0 0 335 160" fill="none" stroke="#dc2626" stroke-width="4"/>
  <text x="350" y="220" class="math-red">angles add together</text>
            """,
            "Complementary angles add to 90 degrees. Supplementary angles add to 180 degrees. Use the total angle sum to solve for the missing angle.",
        )

    if "polygon" in combined:
        return _show_geometry_visual(
            "Polygon Interior Angles Visualization",
            """
  <text x="310" y="44" text-anchor="middle" class="math-label">sum = (n - 2) x 180°</text>
  <polygon points="310,75 470,150 430,280 190,280 150,150" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <line x1="310" y1="75" x2="190" y2="280" stroke="#dc2626" stroke-width="3" stroke-dasharray="8 8"/>
  <line x1="310" y1="75" x2="430" y2="280" stroke="#dc2626" stroke-width="3" stroke-dasharray="8 8"/>
  <text x="310" y="305" text-anchor="middle" class="math-small">split polygon into triangles</text>
            """,
            "A polygon can be split into triangles from one vertex. A polygon with n sides forms n - 2 triangles, and each triangle has 180 degrees.",
        )

    if "sin 0" in combined or "cos 0" in combined or "pythagorean identity" in combined:
        if "pythagorean" in combined:
            identity = "sin²x + cos²x = 1"
        elif "sin 0" in combined:
            identity = "sin(0°) = 0"
        elif "cos 0" in combined:
            identity = "cos(0°) = 1"
        else:
            identity = formula or title
        return _show_geometry_visual(
            "Unit Circle Trig Visualization",
            f"""
  <text x="310" y="44" text-anchor="middle" class="math-label">{identity}</text>
  <line x1="120" y1="175" x2="500" y2="175" stroke="#94a3b8" stroke-width="2"/>
  <line x1="310" y1="60" x2="310" y2="290" stroke="#94a3b8" stroke-width="2"/>
  <circle cx="310" cy="175" r="105" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/>
  <line x1="310" y1="175" x2="415" y2="175" stroke="#dc2626" stroke-width="4"/>
  <circle cx="415" cy="175" r="7" fill="#dc2626"/>
  <text x="425" y="168" class="math-red">(1,0)</text>
            """,
            "On the unit circle at 0 degrees, the point is (1,0). That means cos 0° = 1 and sin 0° = 0. The identity sin²x + cos²x = 1 matches the unit circle radius.",
        )

    return False


def _show_math_lesson_visuals(row):
    is_geometry = _text(row.get("domain")).lower() == "geometry"
    shown_equation = False if is_geometry else _show_equation_plot(row)
    shown_shape = _show_geometry_formula_visual(row) if is_geometry else False

    if not shown_equation and not shown_shape:
        st.caption("No special graph is available for this lesson yet.")


def _show_math_lesson_questions(row):
    questions_df = load_math_questions().fillna("")
    lesson_title = _text(row.get("lesson_title")).lower()
    domain = _text(row.get("domain")).lower()

    lesson_questions = questions_df[
        (questions_df["lesson_title"].apply(lambda value: _text(value).lower()) == lesson_title)
        & (questions_df["domain"].apply(lambda value: _text(value).lower()) == domain)
    ].copy()

    if lesson_questions.empty:
        st.caption("No practice questions are available for this lesson yet.")
        return

    difficulty_order = {"Easy": 0, "Medium": 1}
    lesson_questions["_order"] = lesson_questions["difficulty"].map(difficulty_order).fillna(99)
    lesson_questions = lesson_questions.sort_values(["_order", "difficulty"]).head(2)

    st.write("##### Practice Questions")

    for question_index, (_, question_row) in enumerate(lesson_questions.iterrows(), start=1):
        difficulty = _text(question_row.get("difficulty"))
        st.markdown(f"**Question {question_index} ({difficulty})**")
        st.write(_text(question_row.get("question")))

        options = {
            "A": _text(question_row.get("option_a")),
            "B": _text(question_row.get("option_b")),
            "C": _text(question_row.get("option_c")),
            "D": _text(question_row.get("option_d")),
        }
        option_labels = [f"{letter}. {value}" for letter, value in options.items() if value]
        answer_key = f"math_question_{domain}_{lesson_title}_{difficulty}_{question_index}".replace(" ", "_")
        selected = st.radio(
            "Choose your answer",
            option_labels,
            index=None,
            key=answer_key,
        )

        if selected:
            selected_letter = selected.split(".", 1)[0]
            correct_answer = _text(question_row.get("correct_answer")).upper()
            explanation = _text(question_row.get("explanation"))

            if selected_letter == correct_answer:
                st.success("💋❤️")
            else:
                st.error("Nope 😭, try again pretty Leila ❤️")

            if explanation:
                st.info(explanation)


def _show_english_rule_explanation(row):
    rule_title = _text(row.get("rule_title"))
    explanation_parts = _parts(row.get("explanation"))
    simple_rule = explanation_parts[0] if explanation_parts else "Use this rule to make the sentence clear, correct, and complete."
    arabic_note = next((part for part in explanation_parts[1:] if "Arabic:" in part), "")
    example = _text(row.get("example"))
    tip = _text(row.get("tip"))

    st.write("### Rule")
    st.info(simple_rule)

    st.write("### Beginner Explanation")
    st.write(
        f"Start by asking what job **{rule_title}** does in the sentence. "
        "Then check the exact words around it before choosing an answer."
    )
    if arabic_note:
        st.caption(arabic_note)

    st.write("### How To Solve It")
    steps = [
        "Find the part of the sentence being tested.",
        f"Apply the rule: {simple_rule}",
        "Remove choices that break the rule or create unclear meaning.",
        "Choose the answer that is grammatically correct and easiest to understand.",
    ]
    for index, step in enumerate(steps, start=1):
        st.write(f"{index}. {step}")

    if example:
        st.write("### Example")
        st.info(example)

    st.write("### Expert Check")
    expert_tip = tip or "Check whether the answer is correct in grammar, meaning, and clarity."
    st.success(expert_tip)

    st.write("### Common EST Trap")
    st.warning(
        "Do not choose an answer only because it sounds familiar. EST questions often hide the mistake in agreement, tense, reference, punctuation, or sentence structure."
    )


def _show_english_rule_questions(row):
    try:
        questions_df = load_english_questions().fillna("")
    except FileNotFoundError:
        st.caption("No English practice questions are available yet.")
        return

    lesson_title = _text(row.get("lesson_title")).lower()
    rule_title = _text(row.get("rule_title")).lower()

    rule_questions = questions_df[
        (questions_df["lesson_title"].apply(lambda value: _text(value).lower()) == lesson_title)
        & (questions_df["rule_title"].apply(lambda value: _text(value).lower()) == rule_title)
    ].copy()

    if rule_questions.empty:
        st.caption("No practice questions are available for this rule yet.")
        return

    difficulty_order = {"Easy": 0, "Medium": 1}
    rule_questions["_order"] = rule_questions["difficulty"].map(difficulty_order).fillna(99)
    rule_questions = rule_questions.sort_values(["_order", "difficulty"]).head(2)

    st.write("##### Practice Questions")

    for question_index, (_, question_row) in enumerate(rule_questions.iterrows(), start=1):
        difficulty = _text(question_row.get("difficulty"))
        st.markdown(f"**Question {question_index} ({difficulty})**")
        st.write(_text(question_row.get("question")))

        options = {
            "A": _text(question_row.get("option_a")),
            "B": _text(question_row.get("option_b")),
            "C": _text(question_row.get("option_c")),
            "D": _text(question_row.get("option_d")),
        }
        option_labels = [f"{letter}. {value}" for letter, value in options.items() if value]
        answer_key = f"english_question_{lesson_title}_{rule_title}_{difficulty}_{question_index}".replace(" ", "_")
        selected = st.radio(
            "Choose your answer",
            option_labels,
            index=None,
            key=answer_key,
        )

        if selected:
            selected_letter = selected.split(".", 1)[0]
            correct_answer = _text(question_row.get("correct_answer")).upper()
            explanation = _text(question_row.get("explanation"))

            if selected_letter == correct_answer:
                st.success("💋❤️")
            else:
                st.error("Nope 😭, try again pretty Leila ❤️")

            if explanation:
                st.info(explanation)


def _dedupe_geometry_lessons(df):
    if df.empty or _text(df.iloc[0].get("domain")).lower() != "geometry":
        return df

    def lesson_key(value):
        key = _text(value).lower()
        if key.startswith("similar triangle"):
            return "similar triangles"
        return key

    rows = df.copy()
    rows["_original_order"] = range(len(rows))
    rows["_lesson_key"] = rows["lesson_title"].apply(lesson_key)
    rows["_formula_length"] = rows["formula"].apply(lambda value: len(_text(value)))

    display_titles = (
        rows.sort_values("_original_order")
        .groupby("_lesson_key")["lesson_title"]
        .first()
        .to_dict()
    )

    kept_rows = (
        rows.sort_values(["_lesson_key", "_formula_length"], ascending=[True, False])
        .drop_duplicates("_lesson_key", keep="first")
        .copy()
    )
    kept_rows["lesson_title"] = kept_rows["_lesson_key"].map(display_titles)

    return kept_rows.sort_values("_original_order").drop(
        columns=["_original_order", "_lesson_key", "_formula_length"]
    )


def show_learning():
    st.title("Learning Mode")

    subject = st.selectbox("Choose Subject", ["Math", "English"])

    if subject == "Math":
        _show_math_topics()
    else:
        _show_english_topics()


def _show_math_topics():
    st.subheader("Math Topics")
    _show_math_learning()


def _show_english_topics():
    st.subheader("English Topics")
    _show_english_learning()


def _show_math_learning():
    df = load_math_content().fillna("")
    topic_rows = df[["topic_id", "domain"]].drop_duplicates()
    topic_labels = topic_rows["domain"].tolist()

    selected_topic = st.selectbox("Choose Math Topic", topic_labels)
    filtered = df[df["domain"] == selected_topic]
    filtered = _dedupe_geometry_lessons(filtered)
    st.subheader(selected_topic)

    selected_lesson = st.selectbox("Choose Lesson", filtered["lesson_title"].tolist())
    filtered = df[df["lesson_title"] == selected_lesson]

    for _, row in filtered.iterrows():
        st.divider()
        st.header(_text(row["lesson_title"]))

        domain = _text(row.get("domain"))
        difficulty = _text(row.get("difficulty"))
        if domain or difficulty:
            st.caption(" | ".join(item for item in [domain, difficulty] if item))

        formula = _text(row.get("formula"))
        if formula:
            st.write("##### Formula")
            _show_formula(formula)

        example = _text(row.get("example"))
        if example:
            st.write("##### Example")
            st.info(example)

        st.write("##### Explanation")
        _show_parts(row.get("explanation"))

        _show_math_lesson_visuals(row)

        if st.button(f"Generate AI Explanation: {_text(row['lesson_title'])}"):
            ai_explanation = generate_math_course(_text(row["lesson_title"]))
            st.success("AI explanation generated")
            st.write(ai_explanation)

        _show_math_lesson_questions(row)


def _show_english_learning():
    df = load_english_content().fillna("")
    topic_rows = df[["topic_id", "lesson_title"]].drop_duplicates()
    topic_labels = topic_rows["lesson_title"].tolist()

    selected_topic = st.selectbox("Choose English Topic", topic_labels)
    filtered = df[df["lesson_title"] == selected_topic]
    st.subheader(selected_topic)

    if st.button(f"Generate AI Explanation: {selected_topic}"):
        ai_explanation = generate_english_course(selected_topic)
        st.success("AI explanation generated")
        st.write(ai_explanation)

    for _, row in filtered.iterrows():
        st.divider()

        rule_title = _text(row.get("rule_title"))
        if rule_title:
            st.markdown(f"#### {rule_title}")

        _show_english_rule_explanation(row)
        _show_english_rule_questions(row)
