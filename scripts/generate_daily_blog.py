#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')
BLOG = ROOT / 'blog'
TEMPLATE = BLOG / 'template.html'
INDEX = BLOG / 'index.html'
SITEMAP = ROOT / 'sitemap.xml'

SITE_NAME = 'Free CPT Code Finder'
AUTHOR = 'Graydon Stallard, DO, FACOS, FACS'
MONTH_YEAR = 'June 2026'


@dataclass(frozen=True)
class Topic:
    slug: str
    section: str
    category_label: str
    category_class: str
    title: str
    description: str
    keywords: str
    breadcrumb: str
    summary: str
    read_time: str
    related: List[tuple[str, str]]
    content: str


def asset_prefix(section: str) -> str:
    return '../' if section == 'blog' else '../../'


def build_article(topic: Topic) -> str:
    template = TEMPLATE.read_text()
    article_html = f'''
                <h1>{html.escape(topic.title)}</h1>
                <div class="article-meta">
                    <span class="author">{AUTHOR}</span>
                    <span>•</span>
                    <span>Updated {MONTH_YEAR}</span>
                    <span>•</span>
                    <span>{topic.read_time}</span>
                </div>

                <p>{topic.summary}</p>

{topic.content}

                <section>
                    <h2>Bottom line</h2>
                    <p>{topic.description}</p>
                </section>
    '''.strip()

    related_links = '\n'.join(
        f'<a href="{href}" class="site-card related-inline"><strong class="inline-code-link">{label}</strong></a>'
        for href, label in topic.related
    )

    page = template
    replacements = {
        '{{META_DESC}}': topic.description,
        '{{KEYWORDS}}': topic.keywords,
        '{{FILENAME}}': f'{topic.section}/{topic.slug}.html',
        '{{BREADCRUMB}}': topic.breadcrumb,
        '{{CONTENT}}': article_html,
        '{{RELATED_LINKS}}': related_links,
    }
    for old, new in replacements.items():
        page = page.replace(old, new)

    prefix = asset_prefix(topic.section)
    page = page.replace('../styles/site-theme.css', f'{prefix}styles/site-theme.css')
    page = page.replace('../js/site-chrome.js', f'{prefix}js/site-chrome.js')
    page = page.replace('<title>Free CPT Code Finder</title>', f'<title>{html.escape(topic.title)} | {SITE_NAME}</title>')
    page = page.replace('<meta name="robots" content="noindex, nofollow">', '<meta name="robots" content="index, follow">')
    page = page.replace('<meta name="robots" content="noindex, follow">', '<meta name="robots" content="index, follow">')
    page = page.replace('<meta property="og:title" content="Free CPT Code Finder">', f'<meta property="og:title" content="{html.escape(topic.title)} | {SITE_NAME}">')
    return page


TOPICS = {
    'modifier-24-postop-em': Topic(
        slug='modifier-24-postop-em',
        section='modifiers',
        category_label='Modifier',
        category_class='cat-modifier',
        title='Modifier 24: Unrelated E/M During the Postoperative Period',
        description='When to use modifier 24, when it fails, and how to document unrelated postoperative E/M visits without getting denied.',
        keywords='modifier 24, postoperative E/M, unrelated evaluation and management, global period, modifier 24 examples',
        breadcrumb='Modifier 24',
        summary='Modifier 24 is one of the fastest ways to either save legitimate postoperative E/M revenue or trigger a denial if the note is sloppy. The rule is simple: the visit must be unrelated to the surgery that created the global period.',
        read_time='6 min read',
        related=[
            ('/blog/modifiers/modifier-25-explained.html', 'Modifier 25 Explained'),
            ('/blog/modifiers/modifier-57-explained.html', 'Modifier 57 Explained'),
            ('/blog/guides/global-surgical-package-explained.html', 'Global Surgical Package Guide'),
        ],
        content='''
                <h2>What modifier 24 means</h2>
                <p>Modifier 24 is appended to an E/M service performed during a postoperative global period when that E/M visit is unrelated to the original procedure. Same surgeon, same group, same specialty rules still apply. If the new problem is genuinely separate, modifier 24 tells the payer not to bundle the visit into the prior surgery.</p>

                <h2>When modifier 24 is appropriate</h2>
                <ul>
                    <li>Post-op hernia patient returns for a brand-new gallbladder complaint.</li>
                    <li>Breast surgery follow-up patient is evaluated for unrelated soft tissue infection elsewhere.</li>
                    <li>Recent appendectomy patient is seen for separate thyroid nodule management.</li>
                </ul>

                <h2>When modifier 24 is a bad idea</h2>
                <ul>
                    <li>Routine wound checks</li>
                    <li>Pain expected from the index operation</li>
                    <li>Drain management or expected post-op surveillance</li>
                    <li>Complication management clearly tied to the original surgery</li>
                </ul>

                <blockquote><p><strong>Rule:</strong> if the note reads like post-op care, don\'t dress it up with modifier 24 and hope for magic.</p></blockquote>

                <h2>Documentation that helps</h2>
                <ul>
                    <li>State the original surgery and date.</li>
                    <li>Name the new unrelated problem explicitly in the assessment.</li>
                    <li>Document separate history, exam, and decision making for the unrelated issue.</li>
                    <li>Keep postoperative care discussion distinct from the billable E/M work.</li>
                </ul>

                <h2>Common denial trigger</h2>
                <p>The usual failure is not the modifier itself. It is the note. If the assessment blends expected postoperative follow-up with a minor new issue, the payer will often bundle the whole thing. Split the note cleanly or the claim gets torched.</p>
        '''
    ),
    'trauma-laparotomy-cpt-guide': Topic(
        slug='trauma-laparotomy-cpt-guide',
        section='guides',
        category_label='CPT Guide',
        category_class='cat-guide',
        title='Trauma Laparotomy CPT Coding: What Actually Gets Paid',
        description='A practical trauma laparotomy coding guide covering exploratory laparotomy, bowel resection, splenectomy, packing, and modifier pitfalls.',
        keywords='trauma laparotomy CPT, exploratory laparotomy coding, damage control laparotomy CPT, trauma surgery coding',
        breadcrumb='Trauma Laparotomy Coding',
        summary='Trauma cases get messy fast, and the coding usually gets messy with them. The cleanest approach is to code what was definitively performed, not what felt dramatic in the room.',
        read_time='7 min read',
        related=[
            ('/blog/guides/cpt-code-trauma-surgery.html', 'Trauma Surgery CPT Codes'),
            ('/blog/modifiers/modifier-51-explained.html', 'Modifier 51 Explained'),
            ('/codes/49000.html', 'CPT 49000 Guide'),
        ],
        content='''
                <h2>Start with the real operative work</h2>
                <p>In trauma laparotomy, surgeons often describe the whole case as an exploratory laparotomy. That may be true narratively, but billing follows the definitive procedure hierarchy. If a bowel resection, splenectomy, diaphragm repair, or vascular control was performed, those services typically outrank a simple exploration code.</p>

                <h2>Common coding pattern</h2>
                <ul>
                    <li><strong>49000</strong> when the laparotomy is exploratory without a more definitive separately reportable intra-abdominal procedure.</li>
                    <li><strong>44120/44121</strong> if small bowel resection is performed.</li>
                    <li><strong>38100/38101</strong> or other splenic procedures when spleen work is definitive.</li>
                    <li><strong>49002</strong> for re-exploration when damage control physiology requires planned return.</li>
                </ul>

                <h2>Damage control cases</h2>
                <p>Do not code pure chaos. Code the actual repairs, resections, or packing work documented. If the patient returns for planned re-exploration, the second trip needs its own clear operative note explaining why it was clinically necessary and what new work was done.</p>

                <h2>Modifier traps</h2>
                <ul>
                    <li>Modifier 51 may be payer-driven rather than manually appended.</li>
                    <li>Modifier 59 is not a panic button for every bundled trauma case.</li>
                    <li>Modifier 78 matters for unplanned return to the OR during global period.</li>
                </ul>

                <h2>Best note language</h2>
                <p>List injuries found, definitive repairs performed, sequence of repair, contamination or hemorrhage burden, and whether abdominal closure was completed or intentionally deferred. If your note is vague, the claim will be vague too.</p>
        '''
    ),
    'icd10-postop-complications-guide': Topic(
        slug='icd10-postop-complications-guide',
        section='icd10',
        category_label='ICD-10',
        category_class='cat-icd',
        title='ICD-10 for Postoperative Complications: Stop Using Garbage Diagnoses',
        description='How to code postoperative complications in ICD-10 more accurately, including wound infection, hemorrhage, seroma, and device-related problems.',
        keywords='ICD-10 postoperative complications, surgical site infection ICD-10, postoperative hemorrhage code, seroma ICD-10',
        breadcrumb='Postoperative Complications ICD-10',
        summary='Post-op complication coding gets ugly when the diagnosis is lazy. “Pain after surgery” and “post-op issue” are not serious coding strategies.',
        read_time='6 min read',
        related=[
            ('/blog/icd10/icd10-coding-hernias.html', 'Hernia ICD-10 Guide'),
            ('/blog/guides/global-surgical-package-explained.html', 'Global Package Guide'),
            ('/blog/modifiers/modifier-24-postop-em.html', 'Modifier 24 Guide'),
        ],
        content='''
                <h2>Code the complication, not the vibe</h2>
                <p>When a postoperative patient returns with a real complication, ICD-10 should reflect the specific problem: infection, hemorrhage, seroma, dehiscence, device complication, obstruction, or another defined issue. Vague diagnosis coding weakens medical necessity and makes the chart look careless.</p>

                <h2>Common buckets</h2>
                <ul>
                    <li>Postprocedural infection</li>
                    <li>Postprocedural hemorrhage or hematoma</li>
                    <li>Seroma after procedure</li>
                    <li>Disruption or dehiscence of wound</li>
                    <li>Complication of mesh, graft, or other implanted material</li>
                </ul>

                <h2>Documentation that matters</h2>
                <ul>
                    <li>State whether the issue is expected postoperative change versus true complication.</li>
                    <li>Identify the anatomic site.</li>
                    <li>Link the complication to the prior procedure when clinically supported.</li>
                    <li>Document severity and management plan.</li>
                </ul>

                <blockquote><p><strong>Blunt truth:</strong> if the surgeon says “possible infection” but treats it like a definite infection, the claim and note start fighting each other.</p></blockquote>

                <h2>Why this matters for payment</h2>
                <p>Specific complication coding supports medical necessity for imaging, antibiotics, drainage, return to OR, or unrelated E/M work. Bad diagnosis selection makes clean reimbursement much harder than it needs to be.</p>
        '''
    ),
    'increase-surgical-rvus': Topic(
        slug='increase-surgical-rvus',
        section='rvu',
        category_label='RVU',
        category_class='cat-rvu',
        title='How to Increase Your Surgical RVUs Legally',
        description='A practical surgeon-focused guide to increasing surgical wRVUs through accurate coding, better documentation, and cleaner capture of work already performed.',
        keywords='increase surgical RVUs, improve surgeon wRVUs, surgical productivity, RVU documentation, modifier 22, critical care RVU, surgeon compensation',
        breadcrumb='Increase Surgical RVUs',
        summary='The cleanest way to increase surgical RVUs is not gaming the system. It is capturing the work you already do with accurate CPT selection, complete operative notes, appropriate modifiers, and disciplined E/M documentation.',
        read_time='7 min read',
        related=[
            ('/blog/rvu/understanding-work-rvus.html', 'Understanding Work RVUs'),
            ('/blog/rvu/how-surgeons-get-paid-rvu-salary.html', 'How Surgeons Get Paid'),
            ('/blog/modifiers/modifier-22-explained.html', 'Modifier 22 Explained'),
        ],
        content='''
                <h2>Start with the obvious truth</h2>
                <p>Most surgeons do not need tricks to increase RVUs. They need cleaner capture of work they are already doing. Missed procedures, weak documentation, uncaptured E/M work, and sloppy modifier support leak productivity all year long.</p>

                <h2>Code the definitive procedure</h2>
                <p>A common mistake is coding the case by the narrative label instead of the definitive work. "Exploratory laparotomy" may describe the operation, but if bowel resection, ostomy creation, splenectomy, repair, or other definitive work was performed, the note and coding should reflect that actual work.</p>

                <h2>Document complexity when it is real</h2>
                <p>Modifier 22 does not work because the case felt hard. It works when the note explains substantially greater work in concrete terms: altered anatomy, dense adhesions, reoperative field, infection, bleeding, obesity, radiation change, extra time, or technical difficulty beyond the usual service.</p>

                <h2>Do not miss critical care</h2>
                <p>Surgeons who manage shock, sepsis, respiratory failure, hemorrhage, or ICU-level decision making often under-document critical care. If critical care time is medically necessary, separately documented, and not bundled into the procedure, it should not disappear from the productivity report.</p>

                <h2>Capture legitimate E/M work</h2>
                <ul>
                    <li>Decision for major surgery may require modifier 57 support.</li>
                    <li>Unrelated postoperative E/M may require modifier 24 support.</li>
                    <li>Same-day office procedures may require separate documentation if an E/M service is truly significant and separately identifiable.</li>
                </ul>

                <h2>Respect add-on codes and MPPR rules</h2>
                <p>Add-on codes and multiple procedure payment reduction rules matter. A poorly ordered claim or missed add-on code can distort the value of a case. Build a habit of reviewing complex multi-procedure cases before they leave the chart.</p>

                <h2>Fix the operative note</h2>
                <p>Your coder cannot code what your note does not support. A strong operative note should clearly list procedures performed, anatomy addressed, approach, findings, complexity, implants, reconstruction, closure, complications, and why additional work was medically necessary.</p>

                <h2>Use CPT-level RVU data carefully</h2>
                <p>RVU data is useful for understanding case mix, but it is not a substitute for correct coding. Compare your common cases against CPT-level wRVU values, but remember that payer rules, global periods, modifiers, and bundling edits still control final reporting.</p>

                <blockquote><p><strong>Rule:</strong> increase RVUs by improving accuracy, not by stretching codes past what the documentation supports.</p></blockquote>

                <h2>Practical weekly audit</h2>
                <ul>
                    <li>Review five recent operations with more than one procedure.</li>
                    <li>Check whether the definitive procedure was coded instead of a generic exploration.</li>
                    <li>Look for missed add-on codes.</li>
                    <li>Check whether difficult cases actually document why they were difficult.</li>
                    <li>Compare critical care notes against documented time and medical necessity.</li>
                </ul>

                <h2>Bottom line</h2>
                <p>The best RVU strategy is boring and defensible: accurate CPT selection, complete notes, appropriate modifiers, and routine review of high-value cases. That is where most of the money leaks.</p>
        '''
    ),
    'rvu-90-day-global-surprises': Topic(
        slug='rvu-90-day-global-surprises',
        section='rvu',
        category_label='RVU',
        category_class='cat-rvu',
        title='Why 90-Day Global Procedures Can Fool Your RVU Math',
        description='A surgeon-focused RVU guide explaining why 90-day global procedures look richer than they feel and where post-op work hides inside the value.',
        keywords='90-day global RVU, surgical global period RVU, postoperative work RVU, surgeon productivity',
        breadcrumb='90-Day Global RVU Math',
        summary='A big RVU number can flatter you. It can also lie to you if you ignore how much postoperative work is already baked into a 90-day global code.',
        read_time='5 min read',
        related=[
            ('/blog/rvu/understanding-work-rvus.html', 'Understanding Work RVUs'),
            ('/blog/modifiers/modifier-57-explained.html', 'Modifier 57 Explained'),
            ('/blog/guides/global-surgical-package-explained.html', 'Global Surgical Package Guide'),
        ],
        content='''
                <h2>The hidden issue</h2>
                <p>Surgeons often look at the work RVU on a major procedure and assume it reflects just the operation. It does not. A 90-day global code includes pre-op and post-op physician work that is already bundled into the valuation.</p>

                <h2>What gets buried inside</h2>
                <ul>
                    <li>Immediate preoperative assessment tied to the operation</li>
                    <li>Routine inpatient or outpatient postoperative follow-up</li>
                    <li>Usual post-op decision making and care coordination</li>
                </ul>

                <h2>Why surgeons misread productivity</h2>
                <p>If one surgeon does a high volume of big 90-day cases, the RVU output may look incredible even though a lot of effort is spread across weeks of follow-up. Another surgeon doing fragmented acute care, procedures, and separate E/M work may feel busier with fewer headline RVUs.</p>

                <h2>Where money leaks</h2>
                <ul>
                    <li>Uncaptured modifier 57 visits before major surgery</li>
                    <li>Failure to distinguish unrelated postoperative E/M work</li>
                    <li>Under-documenting procedures that should outrank exploratory work</li>
                </ul>

                <h2>Bottom line for practice owners</h2>
                <p>Do not judge surgeon productivity by raw procedure RVUs alone. Global work distorts everything. If you want a fair view, pair RVU data with case mix, call burden, complication burden, and separate E/M capture.</p>
        '''
    )
}


def update_blog_index(topic: Topic) -> None:
    html_text = INDEX.read_text()
    card = f'''
            <a href="/blog/{topic.section}/{topic.slug}.html" class="article-card">
                <span class="category {topic.category_class}">{topic.category_label}</span>
                <h2>{topic.title}</h2>
                <p>{topic.description}</p>
                <div class="meta">{AUTHOR} &middot; {MONTH_YEAR}</div>
            </a>
'''
    marker = '<div class="articles">'
    html_text = html_text.replace(marker, marker + '\n' + card, 1)
    INDEX.write_text(html_text)


def update_sitemap(topic: Topic) -> None:
    sitemap = SITEMAP.read_text()
    loc = f'https://freecptcodefinder.com/blog/{topic.section}/{topic.slug}.html'
    if loc in sitemap:
        return
    sitemap = sitemap.replace('</urlset>', f'  <url>\n    <loc>{loc}</loc>\n  </url>\n</urlset>')
    SITEMAP.write_text(sitemap)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', required=True, choices=sorted(TOPICS.keys()))
    parser.add_argument('--publish', action='store_true', help='Write the file and update blog index + sitemap.')
    args = parser.parse_args()

    topic = TOPICS[args.topic]
    out = BLOG / topic.section / f'{topic.slug}.html'
    page = build_article(topic)

    if args.publish:
        out.write_text(page)
        update_blog_index(topic)
        update_sitemap(topic)
        print(f'Published {out.relative_to(ROOT)}')
    else:
        print(page)


if __name__ == '__main__':
    main()
