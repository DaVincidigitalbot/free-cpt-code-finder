/**
 * SpecialtyNavigator for FreeCPTCodeFinder
 * Renders specialty hierarchy in the sidebar with drill-down navigation.
 * Specialty → System → Procedure Group → Codes
 * Click a code → adds to CaseBuilder.
 */

class SpecialtyNavigator {
  constructor() {
    this.hierarchy = null;
    this.containerEl = null;
    this.breadcrumbEl = null;
    this.listEl = null;
    this.searchEngine = null;   // ref to UnifiedSearchEngine
    this.caseBuilder = null;    // ref to CaseBuilder
    this.navStack = [];         // breadcrumb trail: [{ label, level, key }]
    this.ready = false;

    // Built-in fallback specialty hierarchy (based on CPT ranges + decision trees)
    this._builtinHierarchy = this._buildFallbackHierarchy();
  }

  /* ── Initialise ─────────────────────────────────────────── */
  async initialize(containerEl, breadcrumbEl) {
    this.containerEl = containerEl;
    this.breadcrumbEl = breadcrumbEl;
    this.listEl = containerEl;

    // Try loading specialty_hierarchy.json; fall back to built-in
    try {
      const resp = await fetch('./specialty_hierarchy.json');
      if (resp.ok) {
        this.hierarchy = await resp.json();
      } else {
        this.hierarchy = this._builtinHierarchy;
      }
    } catch {
      this.hierarchy = this._builtinHierarchy;
    }

    // Enrich with code counts from searchEngine
    if (this.searchEngine && this.searchEngine.ready) {
      this._enrichCounts();
    }

    this.ready = true;
    this.renderRoot();
    console.log('[SpecialtyNavigator] Ready');
  }

  /* ── Built-in fallback hierarchy ────────────────────────── */
  _buildFallbackHierarchy() {
    return {
      specialties: [
        {
          key: 'general_surgery',
          label: 'General Surgery',
          icon: '🔪',
          systems: [
            {
              key: 'hernia',
              label: 'Hernia Repair',
              groups: [
                { label: 'Inguinal Hernia', codes: ['49505','49507','49520','49525','49650','49651'] },
                { label: 'Ventral / Incisional', codes: ['49560','49561','49565','49566','49568','49652','49653','49654','49655','49656','49657'] },
                { label: 'Umbilical', codes: ['49580','49582','49585','49587'] },
                { label: 'Femoral', codes: ['49550','49553','49555','49557'] },
                { label: 'Hiatal / Diaphragmatic', codes: ['43280','43281','43282','43283'] },
              ]
            },
            {
              key: 'gallbladder',
              label: 'Gallbladder & Biliary',
              groups: [
                { label: 'Cholecystectomy', codes: ['47562','47563','47564','47600','47605','47610'] },
                { label: 'Bile Duct', codes: ['47420','47425','47480','47490'] },
              ]
            },
            {
              key: 'appendix',
              label: 'Appendix',
              groups: [
                { label: 'Appendectomy', codes: ['44950','44960','44970'] },
              ]
            },
            {
              key: 'small_bowel',
              label: 'Small Bowel',
              groups: [
                { label: 'Resection & Repair', codes: ['44120','44125','44130','44140','44202','44203'] },
              ]
            },
            {
              key: 'colorectal',
              label: 'Colorectal',
              groups: [
                { label: 'Colectomy', codes: ['44140','44141','44143','44144','44145','44146','44147','44150','44151','44155','44156','44157','44158','44160','44204','44205','44206','44207','44208','44210','44211','44212','44213'] },
                { label: 'Rectal', codes: ['45110','45111','45112','45113','45114','45119','45120','45126','45130','45135','45160','45171','45172','45190','45300','45303','45305','45307','45308','45309','45315','45317','45320','45321','45327','45330','45331','45332','45333','45334','45335','45337','45338','45340','45341','45342','45345','45346','45347','45349','45350','45378','45379','45380','45381','45382','45384','45385','45386','45388','45390','45391','45392','45393','45395','45397','45398','45399'] },
              ]
            },
            {
              key: 'breast',
              label: 'Breast Surgery',
              groups: [
                { label: 'Excision & Biopsy', codes: ['19100','19101','19110','19112','19120','19125','19126'] },
                { label: 'Mastectomy', codes: ['19301','19302','19303','19304','19305','19306','19307'] },
              ]
            },
            {
              key: 'thyroid',
              label: 'Thyroid & Parathyroid',
              groups: [
                { label: 'Thyroidectomy', codes: ['60220','60225','60240','60252','60254','60260','60270','60271'] },
                { label: 'Parathyroid', codes: ['60500','60502','60505'] },
              ]
            },
            {
              key: 'wound',
              label: 'Wound & Soft Tissue',
              groups: [
                { label: 'Debridement', codes: ['11042','11043','11044','11045','11046','11047'] },
                { label: 'Abscess I&D', codes: ['10060','10061','10080','10081','10120','10121','10140','10160','10180'] },
                { label: 'Skin Excision', codes: ['11400','11401','11402','11403','11404','11406','11420','11421','11422','11423','11424','11426','11440','11441','11442','11443','11444','11446','11600','11601','11602','11603','11604','11606','11620','11621','11622','11623','11624','11626','11640','11641','11642','11643','11644','11646'] },
              ]
            },
            {
              key: 'vascular_access',
              label: 'Vascular Access',
              groups: [
                { label: 'Central Lines', codes: ['36555','36556','36557','36558','36560','36561','36563','36565','36566','36568','36569','36570','36571','36578','36580','36581','36582','36583','36584','36585','36589','36590'] },
              ]
            },
            {
              key: 'endoscopy',
              label: 'Endoscopy',
              groups: [
                { label: 'Upper GI', codes: ['43235','43236','43237','43238','43239','43241','43242','43243','43244','43245','43246','43247','43248','43249','43250','43251','43252','43253','43254','43255','43257','43259','43260','43261','43262','43263','43264','43265','43266','43270','43274','43275','43276','43277','43278'] },
                { label: 'Colonoscopy', codes: ['45378','45379','45380','45381','45382','45384','45385','45386','45388','45390','45391','45392','45393','45395','45397','45398','45399'] },
              ]
            },
          ]
        },
        {
          key: 'trauma',
          label: 'Trauma Surgery',
          icon: '🚑',
          systems: [
            {
              key: 'abdominal_trauma',
              label: 'Abdominal Trauma',
              groups: [
                { label: 'Exploratory Laparotomy', codes: ['49000','49002','49010','49020'] },
                { label: 'Spleen', codes: ['38100','38101','38102','38115','38120'] },
                { label: 'Liver', codes: ['47350','47360','47361','47362'] },
                { label: 'Diaphragm', codes: ['39501','39503','39540','39541','39545'] },
              ]
            },
            {
              key: 'chest_trauma',
              label: 'Chest Trauma',
              groups: [
                { label: 'Thoracotomy', codes: ['32110','32120','32124','32140','32141','32150','32160'] },
                { label: 'Chest Tube', codes: ['32551','32552','32553','32554','32555','32556','32557'] },
              ]
            },
          ]
        },
        {
          key: 'critical_care',
          label: 'Critical Care',
          icon: '🏥',
          systems: [
            {
              key: 'cc_services',
              label: 'Critical Care Services',
              groups: [
                { label: 'Critical Care', codes: ['99291','99292'] },
                { label: 'Ventilation Management', codes: ['94002','94003','94004','94005'] },
              ]
            },
            {
              key: 'airway',
              label: 'Airway Management',
              groups: [
                { label: 'Intubation / Tracheostomy', codes: ['31500','31600','31601','31603','31605','31610'] },
              ]
            },
          ]
        },
        {
          key: 'em',
          label: 'E/M Services',
          icon: '📋',
          systems: [
            {
              key: 'office',
              label: 'Office / Outpatient',
              groups: [
                { label: 'New Patient', codes: ['99202','99203','99204','99205'] },
                { label: 'Established Patient', codes: ['99211','99212','99213','99214','99215'] },
              ]
            },
            {
              key: 'inpatient',
              label: 'Hospital Inpatient',
              groups: [
                { label: 'Initial Hospital Care', codes: ['99221','99222','99223'] },
                { label: 'Subsequent Hospital Care', codes: ['99231','99232','99233'] },
                { label: 'Observation', codes: ['99234','99235','99236'] },
                { label: 'Discharge', codes: ['99238','99239'] },
              ]
            },
            {
              key: 'consult',
              label: 'Consultations',
              groups: [
                { label: 'Office Consult', codes: ['99241','99242','99243','99244','99245'] },
                { label: 'Inpatient Consult', codes: ['99251','99252','99253','99254','99255'] },
              ]
            },
          ]
        },
        {
          key: 'hpb',
          label: 'HPB Surgery',
          icon: '🫁',
          systems: [
            {
              key: 'liver_surg',
              label: 'Liver',
              groups: [
                { label: 'Hepatectomy', codes: ['47120','47122','47125','47130'] },
                { label: 'Liver Ablation', codes: ['47380','47381','47382','47383'] },
              ]
            },
            {
              key: 'pancreas',
              label: 'Pancreas',
              groups: [
                { label: 'Pancreatectomy', codes: ['48140','48145','48146','48148','48150','48152','48153','48154','48155'] },
                { label: 'Whipple', codes: ['48150','48152','48153','48154'] },
              ]
            },
          ]
        },
        {
          key: 'cardiothoracic',
          label: 'Cardiothoracic',
          icon: '❤️',
          systems: [
            {
              key: 'cardiac',
              label: 'Cardiac',
              groups: [
                { label: 'CABG', codes: ['33510','33511','33512','33513','33514','33516','33517','33518','33519','33521','33522','33523','33530','33533','33534','33535','33536'] },
                { label: 'Valve', codes: ['33400','33401','33403','33404','33405','33406','33410','33411','33412','33413','33414','33415','33416','33417','33420','33422','33425','33426','33427','33430'] },
              ]
            },
            {
              key: 'thoracic',
              label: 'Thoracic',
              groups: [
                { label: 'Lung Resection', codes: ['32440','32442','32445','32480','32482','32484','32486','32488','32491','32501','32503','32504','32505','32506','32507'] },
                { label: 'VATS', codes: ['32601','32604','32606','32607','32608','32609','32650','32651','32652','32653','32654','32655','32656','32658','32659','32661','32662','32663','32664','32665','32666','32667','32668','32669','32670','32671','32672','32673','32674'] },
              ]
            },
          ]
        },
        {
          key: 'vascular',
          label: 'Vascular Surgery',
          icon: '🩸',
          systems: [
            {
              key: 'carotid',
              label: 'Carotid',
              groups: [
                { label: 'Carotid Endarterectomy', codes: ['35301','35390'] },
              ]
            },
            {
              key: 'peripheral',
              label: 'Peripheral Vascular',
              groups: [
                { label: 'Bypass', codes: ['35556','35558','35566','35571','35583','35585','35587'] },
                { label: 'Embolectomy', codes: ['34001','34051','34101','34111','34151','34201','34203'] },
              ]
            },
            {
              key: 'aortic',
              label: 'Aortic',
              groups: [
                { label: 'Open AAA Repair', codes: ['35081','35082','35091','35092','35102','35103'] },
                { label: 'EVAR', codes: ['34800','34802','34803','34804','34805','34806','34812','34813','34820','34825','34826','34830','34831','34832','34833','34834'] },
              ]
            },
          ]
        },
        {
          key: 'ortho',
          label: 'Orthopedic',
          icon: '🦴',
          systems: [
            {
              key: 'fracture',
              label: 'Fracture Care',
              groups: [
                { label: 'Closed Treatment', codes: ['25600','25605','25606','25607','25608','25609','27230','27232','27235','27236','27238','27240','27244','27245','27246'] },
                { label: 'Open Treatment', codes: ['25607','25608','25609','27236','27244','27245','27246','27269'] },
              ]
            },
            {
              key: 'joint',
              label: 'Joint',
              groups: [
                { label: 'Arthroplasty', codes: ['27130','27132','27134','27137','27138','27236','27447'] },
                { label: 'Arthroscopy', codes: ['29805','29806','29807','29819','29820','29821','29822','29823','29824','29825','29826','29827','29828','29830','29834','29835','29836','29837','29838','29840','29843','29844','29845','29846','29847','29848','29850','29851','29855','29856','29860','29861','29862','29863','29866','29867','29868','29870','29871','29873','29874','29875','29876','29877','29879','29880','29881','29882','29883','29884','29885','29886','29887','29888','29889'] },
              ]
            },
          ]
        },
        {
          key: 'neurosurgery',
          label: 'Neurosurgery',
          icon: '🧠',
          systems: [
            {
              key: 'cranial',
              label: 'Cranial',
              groups: [
                { label: 'Craniotomy', codes: ['61304','61305','61312','61313','61314','61315','61320','61321','61322','61323','61330','61332','61333','61340','61343','61345'] },
                { label: 'Burr Hole', codes: ['61150','61151','61154','61156'] },
              ]
            },
            {
              key: 'spine',
              label: 'Spine',
              groups: [
                { label: 'Laminectomy', codes: ['63001','63003','63005','63011','63012','63015','63016','63017','63020','63030','63035','63040','63042','63043','63044','63045','63046','63047','63048','63050','63051','63055','63056','63057'] },
                { label: 'Fusion', codes: ['22551','22552','22554','22556','22558','22585','22590','22595','22600','22610','22612','22614','22630','22632','22633','22634'] },
              ]
            },
          ]
        },
        {
          key: 'ent',
          label: 'ENT / Otolaryngology',
          icon: '👂',
          systems: [
            {
              key: 'sinus',
              label: 'Sinus',
              groups: [
                { label: 'FESS', codes: ['31231','31233','31235','31237','31238','31239','31240','31253','31254','31255','31256','31257','31258','31259','31267','31276','31287','31288','31290','31291','31292','31293','31294','31295','31296','31297','31298','31299'] },
              ]
            },
            {
              key: 'tonsil',
              label: 'Tonsil & Adenoid',
              groups: [
                { label: 'Tonsillectomy', codes: ['42820','42821','42825','42826','42830','42831','42835','42836'] },
              ]
            },
          ]
        },
        {
          key: 'obgyn',
          label: 'OB/GYN',
          icon: '👶',
          systems: [
            {
              key: 'gyn',
              label: 'Gynecologic',
              groups: [
                { label: 'Hysterectomy', codes: ['58150','58152','58180','58200','58210','58260','58262','58263','58267','58270','58275','58280','58285','58290','58291','58292','58293','58294','58541','58542','58543','58544','58548','58550','58552','58553','58554','58570','58571','58572','58573'] },
                { label: 'Oophorectomy / Salpingectomy', codes: ['58661','58662','58670','58671','58700','58720','58900','58920','58925','58940','58943'] },
              ]
            },
            {
              key: 'obstetric',
              label: 'Obstetric',
              groups: [
                { label: 'Cesarean Section', codes: ['59510','59514','59515','59525','59610','59612','59614','59618','59620','59622'] },
              ]
            },
          ]
        },
        {
          key: 'urology',
          label: 'Urology',
          icon: '💧',
          systems: [
            {
              key: 'kidney',
              label: 'Kidney',
              groups: [
                { label: 'Nephrectomy', codes: ['50220','50225','50230','50234','50236','50240','50543','50545','50546','50547','50548'] },
              ]
            },
            {
              key: 'bladder',
              label: 'Bladder',
              groups: [
                { label: 'Cystectomy', codes: ['51550','51555','51565','51570','51575','51580','51585','51590','51595','51596','51597'] },
                { label: 'Cystoscopy', codes: ['52000','52001','52005','52007','52204','52214','52224','52234','52235','52240'] },
              ]
            },
          ]
        },
      ]
    };
  }

  /* ── Enrich counts from search engine ───────────────────── */
  _enrichCounts() {
    if (!this.searchEngine) return;
    const allCPT = this.searchEngine.getAllCPT();
    const codeSet = new Set(allCPT.map(c => c.code));

    for (const spec of this.hierarchy.specialties) {
      let specCount = 0;
      for (const sys of spec.systems || []) {
        let sysCount = 0;
        for (const grp of sys.groups || []) {
          const valid = grp.codes.filter(c => codeSet.has(c));
          grp._validCount = valid.length;
          sysCount += valid.length;
        }
        sys._count = sysCount;
        specCount += sysCount;
      }
      spec._count = specCount;
    }
  }

  /* ── Rendering ──────────────────────────────────────────── */
  renderRoot() {
    this.navStack = [];
    this._renderBreadcrumb();
    this._renderSpecialties();
  }

  _renderSpecialties() {
    if (!this.listEl) return;
    this.listEl.innerHTML = '';

    for (const spec of this.hierarchy.specialties) {
      const btn = document.createElement('button');
      btn.className = 'specialty-btn';
      btn.innerHTML = `
        <span class="specialty-btn__icon">${spec.icon || '📁'}</span>
        <span>${spec.label}</span>
        ${spec._count != null ? `<span class="specialty-btn__count">${spec._count}</span>` : ''}
      `;
      btn.addEventListener('click', () => this._drillIntoSpecialty(spec));
      this.listEl.appendChild(btn);
    }
  }

  _drillIntoSpecialty(spec) {
    this.navStack = [{ label: spec.label, level: 'specialty', data: spec }];
    this._renderBreadcrumb();
    this._renderSystems(spec.systems || []);
  }

  _renderSystems(systems) {
    if (!this.listEl) return;
    this.listEl.innerHTML = '';

    for (const sys of systems) {
      const btn = document.createElement('button');
      btn.className = 'specialty-sub-item';
      btn.innerHTML = `
        <span>${sys.label}</span>
        ${sys._count != null ? `<span class="specialty-btn__count">${sys._count}</span>` : ''}
      `;
      btn.addEventListener('click', () => this._drillIntoSystem(sys));
      this.listEl.appendChild(btn);
    }
  }

  _drillIntoSystem(sys) {
    this.navStack.push({ label: sys.label, level: 'system', data: sys });
    this._renderBreadcrumb();
    this._renderGroups(sys.groups || []);
  }

  _renderGroups(groups) {
    if (!this.listEl) return;
    this.listEl.innerHTML = '';

    for (const grp of groups) {
      const btn = document.createElement('button');
      btn.className = 'specialty-sub-item';
      btn.innerHTML = `
        <span>${grp.label}</span>
        <span class="specialty-btn__count">${grp.codes.length}</span>
      `;
      btn.addEventListener('click', () => this._drillIntoGroup(grp));
      this.listEl.appendChild(btn);
    }
  }

  _drillIntoGroup(grp) {
    this.navStack.push({ label: grp.label, level: 'group', data: grp });
    this._renderBreadcrumb();
    this._renderCodes(grp.codes);
  }

  _renderCodes(codes) {
    if (!this.listEl) return;
    this.listEl.innerHTML = '';

    for (const code of codes) {
      const cptData = this.searchEngine ? this.searchEngine.getCPT(code) : null;
      const btn = document.createElement('button');
      btn.className = 'specialty-sub-item';

      if (cptData) {
        const desc = cptData.description.length > 50
          ? cptData.description.slice(0, 50) + '...'
          : cptData.description;
        btn.innerHTML = `
          <span class="code-tag">${code}</span>
          <span style="flex:1;font-size:0.75rem;color:var(--text-secondary)">${desc}</span>
          <span style="font-family:var(--font-mono);font-size:0.6875rem;color:var(--info)">${cptData.wRVU.toFixed(2)}</span>
        `;
      } else {
        btn.innerHTML = `<span class="code-tag">${code}</span>`;
      }

      btn.addEventListener('click', () => {
        if (this.caseBuilder && cptData) {
          this.caseBuilder.addProcedure(cptData);
        } else if (this.caseBuilder) {
          this.caseBuilder.addProcedure({ code, description: '', wRVU: 0, type: 'cpt' });
        }
      });
      this.listEl.appendChild(btn);
    }
  }

  /* ── Breadcrumb ─────────────────────────────────────────── */
  _renderBreadcrumb() {
    if (!this.breadcrumbEl) return;
    this.breadcrumbEl.innerHTML = '';

    // Root
    const root = document.createElement('button');
    root.className = 'breadcrumb-item';
    root.textContent = 'Specialties';
    root.addEventListener('click', () => this.renderRoot());
    this.breadcrumbEl.appendChild(root);

    for (let i = 0; i < this.navStack.length; i++) {
      const sep = document.createElement('span');
      sep.className = 'breadcrumb-sep';
      sep.textContent = '›';
      this.breadcrumbEl.appendChild(sep);

      const crumb = document.createElement('button');
      crumb.className = 'breadcrumb-item';
      crumb.textContent = this.navStack[i].label;
      const idx = i;
      crumb.addEventListener('click', () => this._navigateTo(idx));
      this.breadcrumbEl.appendChild(crumb);
    }
  }

  _navigateTo(idx) {
    const entry = this.navStack[idx];
    this.navStack = this.navStack.slice(0, idx + 1);
    this._renderBreadcrumb();

    if (entry.level === 'specialty') {
      this._renderSystems(entry.data.systems || []);
    } else if (entry.level === 'system') {
      this._renderGroups(entry.data.groups || []);
    } else if (entry.level === 'group') {
      this._renderCodes(entry.data.codes);
    }
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = SpecialtyNavigator;
}
