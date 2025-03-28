equations_of_state = {'jcpds4':{
                        'name': 'Legacy JCPDS4 style Birch Murnaghan 3-rd order <br>with temperature-dependent bulk modulus',
                        'reference':'',
                        'comment':'',
                        'params':{ 
                        'V_0':      {'symbol':u'V<sub>0</sub>',
                                     'desc':u'Volume at P=10⁵ Pa, T=300 K',
                                     'unit':u'Å³'}, 
                        'K_0':      {'symbol':u'K<sub>0</sub>',
                                     'desc':u'Isothermal bulk modulus at P=10⁵ Pa, T=300 K',
                                     'unit':u'GPa'}, 
                        'Kprime_0': {'symbol':u"K'<sub>0</sub>",
                                     'desc':u'Pressure derivative of K<sub>0</sub>',
                                     'unit':u''}, 
                        'dk0dt': {'symbol':u'dK<sub>0</sub>/dT',
                                     'desc':u'Temperature derivative of K<sub>0</sub>',
                                     'unit':u'GPa/K'}, 
                        'dk0pdt': {'symbol':u"dK'<sub>0</sub>/dT",
                                     'desc':u"Temperature derivative of K'<sub>0</sub>",
                                     'unit':u'1/K'},
                        'alpha_t0': {'symbol':u'α<sub>T</sub>',
                                     'desc':u'Thermal expansion coefficient',
                                     'unit':u'1/K'}, 
                        'd_alpha_dt': {'symbol':u'dα<sub>T</sub>/dT',
                                     'desc':u'Temperature derivative of the thermal expansion coefficient',
                                     'unit':u'1/K²'}
                        }},

                    'bm3':{
                        'name': 'Isothermal Birch Murnaghan 3-rd order',
                        'reference':'',
                        'comment':'',
                        'params':{ 
                        
                        'V_0':      {'symbol':u'V<sub>0</sub>',
                                     'desc':u'Volume at P=10⁵ Pa, T=300 K',
                                     'unit':u'm³/mol'}, 
                        'K_0':      {'symbol':u'K<sub>0</sub>',
                                     'desc':u'Isothermal bulk modulus at P=10⁵ Pa, T=300 K',
                                     'unit':u'Pa'}, 
                        'Kprime_0': {'symbol':u"K'<sub>0</sub>",
                                     'desc':u'Pressure derivative of K<sub>0</sub>',
                                     'unit':u''}
                        }},
                    'slb2':{
                        'name': 'Stixrude Lithgow-Bertelloni 2-nd order',
                        'reference':'L. Stixrude and C. Lithgow-Bertelloni, Thermodynamics of <br> \
                                     mantle minerals – I. Physical properties. <br> \
                                     Geophys. J. Int. (2005) 162, 610–632',
                        'comment':'',
                        'params':{ 
                        
                        'V_0':      {'symbol':u'V<sub>0</sub>',
                                     'desc':u'Volume at P=10⁵ Pa, T=300 K',
                                     'unit':u'm³/mol'}, 
                        'K_0':      {'symbol':u'K<sub>0</sub>',
                                     'desc':u'Isothermal bulk modulus at P=10⁵ Pa, T=300 K',
                                     'unit':u'Pa'}, 
                        'Kprime_0': {'symbol':u"K'<sub>0</sub>",
                                     'desc':u'Pressure derivative of K<sub>0</sub>',
                                     'unit':u''}, 
                        'G_0':      {'symbol':u'G<sub>0</sub>',
                                     'desc':u'Shear modulus at P=10⁵ Pa, T=300 K',
                                     'unit':u'Pa'}, 
                        'Gprime_0': {'symbol':u"G'<sub>0</sub>",
                                     'desc':u'Pressure derivative of G<sub>0</sub>',
                                     'unit':u''}, 
                        'molar_mass': {'symbol':u'μ',
                                     'desc':u'Mass per mole formula unit',
                                     'unit':u'Kg/mol',
                                     'default':0.05}, 
                        'n':        {'symbol':u'n',
                                     'desc':u'Number of atoms per formula unit',
                                     'unit':u'',
                                     'default':1}, 
                        'Debye_0':  {'symbol':u'θ<sub>0</sub>',
                                     'desc':u'Debye Temperature',
                                     'unit':u'K',
                                     'default':300}, 
                        'grueneisen_0': {'symbol':u'γ<sub>0</sub>',
                                     'desc':u'Gruneisen parameter at P=10⁵ Pa, T=300 K',
                                     'unit':u'',
                                     'default':1}, 
                        'q_0':      {'symbol':u'q<sub>0</sub>',
                                     'desc':u'Logarithmic volume derivative of the Gr€uneisen parameter',
                                     'unit':u'',
                                     'default':1}, 
                        'eta_s_0':  {'symbol':u'η<sub>S</sub><sub>0</sub>',
                                     'desc':u'Shear strain derivative of the Gruneisen parameter',
                                     'unit':u''}
                        }},

                        'dewaele2006': {
                            'name': 'Dewaele et al. (2006) Mie–Grüneisen–Debye EOS',
                            'reference': 'Dewaele et al., Phys. Rev. Lett. 97, 215504 (2006)',
                            'comment': ('EOS formulation using a 300 K Vinet baseline with a thermal-pressure model '
                                        'that is defined to be zero at 300 K. Bulk modulus is specified in GPa.'),
                            'params': {
                                # --- Baseline (Vinet) parameters ---
                                'V_0': {
                                    'symbol': u'V<sub>0</sub>',
                                    'desc': u'Volume at reference P=10⁵ Pa, T=300 K',
                                    'unit': u'cm³/mol',
                                    'default': 6.76e-6
                                },
                                'K_0': {
                                    'symbol': u'K<sub>0</sub>',
                                    'desc': u'Isothermal bulk modulus at reference conditions (300 K)',
                                    'unit': u'GPa',
                                    'default': 1.634e11
                                },
                                'Kprime_0': {
                                    'symbol': u"K'<sub>0</sub>",
                                    'desc': u'Pressure derivative of K<sub>0</sub>',
                                    'unit': u'',
                                    'default': 5.38
                                },
                                # --- Thermal model parameters ---
                                'theta_0': {
                                    'symbol': u'\u03B8<sub>0</sub>',
                                    'desc': u'Debye temperature at reference volume',
                                    'unit': u'K',
                                    'default': 417.0
                                },
                                'gamma_0': {
                                    'symbol': u'\u03B3<sub>0</sub>',
                                    'desc': u'Grüneisen parameter at P=10⁵ Pa, T=300 K',
                                    'unit': u'',
                                    'default': 1.875
                                },
                                'gamma_inf': {
                                    'symbol': u'\u03B3<sub>\u221E</sub>',
                                    'desc': u'High-compression limit of the Grüneisen parameter',
                                    'unit': u'',
                                    'default': 1.305
                                },
                                'beta': {
                                    'symbol': u'\u03B2',
                                    'desc': u'Exponent controlling the volume dependence of \u03B3 (β = γ₀/(γ₀−γ∞))',
                                    'unit': u'',
                                    'default': 3.289
                                },
                                'a0': {
                                    'symbol': u'a<sub>0</sub>',
                                    'desc': u'Coefficient for anharmonic term',
                                    'unit': u'K<sup>-1</sup>',
                                    'default': 3.7e-5
                                },
                                'm_anh': {
                                    'symbol': u'm',
                                    'desc': u'Exponent for anharmonic term',
                                    'unit': u'',
                                    'default': 1.87
                                },
                                'e0': {
                                    'symbol': u'e<sub>0</sub>',
                                    'desc': u'Coefficient for electronic term',
                                    'unit': u'K<sup>-1</sup>',
                                    'default': 1.95e-4
                                },
                                'g_el': {
                                    'symbol': u'g',
                                    'desc': u'Exponent for electronic term',
                                    'unit': u'',
                                    'default': 1.339
                                },
                                # --- Composition parameters ---
                                'molar_mass': {
                                    'symbol': u'\u03BC',
                                    'desc': u'Mass per mole of formula units',
                                    'unit': u'kg/mol',
                                    # For pure Fe: 55.845 g/mol = 5.5845e-2 kg/mol
                                    'default': 5.5845e-2
                                },
                                'n': {
                                    'symbol': u'n',
                                    'desc': u'Number of atoms per formula unit',
                                    'unit': u'',
                                    'default': 1
                                }
                            }
                        }
                    
                    }