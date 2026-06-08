/**
 * 페이지 렌더링 및 이벤트 핸들러 모음
 */

const pages = {
    async renderHome() {
        const html = await utils.loadTemplate('home');
        if (state.currentPage !== '/' && state.currentPage !== '/home') return;
        const app = document.getElementById('app');
        app.innerHTML = html;
        
        const actions = document.getElementById('home-actions');
        if (!state.user) {
            actions.innerHTML = '<button onclick="navigate(\'/login\')">로그인하여 시작하기</button>';
        } else if (state.user.role === 'pending') {
            actions.innerHTML = '<p>관리자의 승인을 기다리는 중입니다.</p>';
        } else {
            actions.innerHTML = '<button onclick="navigate(\'/patients\')">환자 목록 보기</button>';
        }
    },

    async renderLogin() {
        const html = await utils.loadTemplate('login');
        document.getElementById('app').innerHTML = html;
    },

    async renderSignup() {
        const html = await utils.loadTemplate('signup');
        document.getElementById('app').innerHTML = html;
        
        const phoneInput = document.getElementById('signup-phone');
        if (phoneInput) {
            phoneInput.addEventListener('input', (e) => utils.handlePhoneInput(e));
        }

        // 국적 선택에 따른 성/이름/미들네임 입력 제어
        const nationalitySelect = document.getElementById('signup-nationality');
        const lastNameInput = document.getElementById('signup-last-name');
        const middleNameContainer = document.getElementById('signup-middle-name-container');
        const middleNameInput = document.getElementById('signup-middle-name');
        const passwordInput = document.getElementById('signup-password');
        const confirmInput = document.getElementById('signup-password-confirm');
        const passwordError = document.getElementById('signup-password-error');
        const employeeNumberInput = document.getElementById('signup-employee-number');
        const employeeNumberError = document.getElementById('signup-employee-number-error');

        const isKoreanMode = () => {
            return !nationalitySelect || nationalitySelect.value === 'korean';
        };

        const checkPasswordMatch = () => {
            if (!passwordInput || !confirmInput || !passwordError) return;
            const password = passwordInput.value;
            const confirm = confirmInput.value;

            if (!confirm) {
                passwordError.style.display = 'none';
                return;
            }

            if (password !== confirm) {
                passwordError.textContent = isKoreanMode() ? '비밀번호가 일치하지 않습니다.' : 'Passwords do not match.';
                passwordError.style.color = 'var(--danger-color)';
                passwordError.style.display = 'block';
            } else {
                passwordError.textContent = isKoreanMode() ? '비밀번호가 일치합니다.' : 'Passwords match.';
                passwordError.style.color = 'var(--secondary-color)';
                passwordError.style.display = 'block';
            }
        };

        const checkEmployeeNumber = () => {
            if (!employeeNumberInput || !employeeNumberError) return;
            const val = employeeNumberInput.value;
            if (val.length > 0 && val.length < 8) {
                employeeNumberError.textContent = isKoreanMode() ? '사번은 8자리 숫자여야 합니다.' : 'Employee ID must be an 8-digit number.';
                employeeNumberError.style.display = 'block';
            } else {
                employeeNumberError.style.display = 'none';
            }
        };

        if (nationalitySelect && lastNameInput && middleNameContainer) {
            const handleNationalityChange = (val) => {
                const lastNameContainer = document.getElementById('signup-last-name-container');
                const firstNameContainer = document.getElementById('signup-first-name-container');
                const firstNameInput = document.getElementById('signup-first-name');
                const lastNameLabel = document.getElementById('signup-last-name-label');
                const firstNameLabel = document.getElementById('signup-first-name-label');
                const middleNameLabel = document.getElementById('signup-middle-name-label');
                
                const lastNameCheckboxContainer = document.getElementById('signup-last-name-checkbox-container');
                const middleNameCheckboxContainer = document.getElementById('signup-middle-name-checkbox-container');
                const lastNameUseCheckbox = document.getElementById('signup-last-name-use');
                const middleNameUseCheckbox = document.getElementById('signup-middle-name-use');

                // DOM 요소 참조 및 텍스트/플레이스홀더 변경 도우미 함수
                const el = (id) => document.getElementById(id);
                const txt = (id, text) => { const item = el(id); if (item) item.textContent = text; };
                const ph = (id, value) => { const item = el(id); if (item) item.placeholder = value; };

                if (val === 'korean') {
                    // 내국인: 성(1) -> 이름(2) 순서, 크기는 동일하게 (flex: 1)
                    if (lastNameContainer) {
                        lastNameContainer.style.order = '1';
                        lastNameContainer.style.flex = '1';
                    }
                    if (firstNameContainer) {
                        firstNameContainer.style.order = '2';
                        firstNameContainer.style.flex = '1';
                    }
                    if (middleNameContainer) {
                        middleNameContainer.style.order = '3';
                    }
                    
                    lastNameInput.required = true;
                    lastNameInput.disabled = false;
                    lastNameInput.style.backgroundColor = '#fff';
                    lastNameInput.placeholder = '성';
                    if (firstNameInput) firstNameInput.placeholder = '이름';
                    
                    if (lastNameLabel) lastNameLabel.textContent = '성';
                    if (firstNameLabel) firstNameLabel.textContent = '이름';
                    
                    middleNameContainer.style.display = 'none';
                    if (middleNameInput) {
                        middleNameInput.value = '';
                        middleNameInput.disabled = true;
                        middleNameInput.style.backgroundColor = '#eee';
                    }

                    if (lastNameCheckboxContainer) lastNameCheckboxContainer.style.display = 'none';
                    if (middleNameCheckboxContainer) middleNameCheckboxContainer.style.display = 'none';

                    // 한국어 번역 적용
                    txt('signup-title', '회원가입');
                    txt('signup-email-label', '이메일');
                    ph('signup-email-id', '이메일 아이디');
                    ph('signup-email-domain', '도메인 입력');
                    txt('signup-email-domain-custom-option', '직접 입력');
                    txt('signup-email-check-btn', '중복 확인');
                    txt('signup-nationality-label', '구분');
                    txt('signup-nationality-korean-option', '내국인');
                    txt('signup-nationality-foreigner-option', '외국인');
                    txt('signup-department-label', '부서');
                    txt('signup-department-default-option', '부서 선택');
                    txt('signup-department-dev-option', '개발팀');
                    txt('signup-department-med-option', '의료진');
                    txt('signup-department-res-option', '연구진');
                    txt('signup-gender-label', '성별');
                    txt('signup-gender-default-option', '성별 선택');
                    txt('signup-gender-male-option', '남성');
                    txt('signup-gender-female-option', '여성');
                    txt('signup-phone-label', '전화번호');
                    ph('signup-phone', '전화번호 (예: 010-1234-5678)');
                    txt('signup-employee-number-label', '사번');
                    ph('signup-employee-number', '사번 (8자리 숫자)');
                    txt('signup-password-label', '비밀번호');
                    ph('signup-password', '비밀번호');
                    txt('signup-password-confirm-label', '비밀번호 확인');
                    ph('signup-password-confirm', '비밀번호 확인');
                    txt('signup-submit-btn', '가입하기');
                    txt('signup-cancel-btn', '취소');
                    
                    txt('signup-last-name-use-label', '있음');
                    txt('signup-middle-name-use-label', '있음');
                } else {
                    // 외국인: 이름(1) -> 미들네임(2) -> 성(3) 순서 (First Name -> Middle Name -> Last Name), 3칸 동일하게
                    if (firstNameContainer) {
                        firstNameContainer.style.order = '1';
                        firstNameContainer.style.flex = '1';
                    }
                    if (middleNameContainer) {
                        middleNameContainer.style.order = '2';
                        middleNameContainer.style.flex = '1';
                    }
                    if (lastNameContainer) {
                        lastNameContainer.style.order = '3';
                        lastNameContainer.style.flex = '1';
                    }
                    
                    lastNameInput.required = false;
                    lastNameInput.placeholder = 'Last Name (Optional)';
                    if (firstNameInput) firstNameInput.placeholder = 'First Name';
                    if (middleNameInput) middleNameInput.placeholder = 'Middle Name (Optional)';
                    
                    if (lastNameLabel) lastNameLabel.textContent = 'Last Name';
                    if (firstNameLabel) firstNameLabel.textContent = 'First Name';
                    if (middleNameLabel) middleNameLabel.textContent = 'Middle Name';
                    
                    middleNameContainer.style.display = 'block';

                    // 외국인은 체크박스로 입력 여부를 선택해야 쓸 수 있게 함
                    if (lastNameCheckboxContainer) lastNameCheckboxContainer.style.display = 'flex';
                    if (middleNameCheckboxContainer) middleNameCheckboxContainer.style.display = 'flex';

                    if (lastNameUseCheckbox) {
                        lastNameInput.disabled = !lastNameUseCheckbox.checked;
                        lastNameInput.style.backgroundColor = lastNameUseCheckbox.checked ? '#fff' : '#eee';
                    }
                    if (middleNameUseCheckbox) {
                        middleNameInput.disabled = !middleNameUseCheckbox.checked;
                        middleNameInput.style.backgroundColor = middleNameUseCheckbox.checked ? '#fff' : '#eee';
                    }

                    // 영어 번역 적용
                    txt('signup-title', 'Sign Up');
                    txt('signup-email-label', 'Email');
                    ph('signup-email-id', 'Email ID');
                    ph('signup-email-domain', 'Domain');
                    txt('signup-email-domain-custom-option', 'Custom domain');
                    txt('signup-email-check-btn', 'Check');
                    txt('signup-nationality-label', 'Type');
                    txt('signup-nationality-korean-option', 'Korean');
                    txt('signup-nationality-foreigner-option', 'Foreigner');
                    txt('signup-department-label', 'Department');
                    txt('signup-department-default-option', 'Select Department');
                    txt('signup-department-dev-option', 'Developer');
                    txt('signup-department-med-option', 'Medical Team');
                    txt('signup-department-res-option', 'Researcher');
                    txt('signup-gender-label', 'Gender');
                    txt('signup-gender-default-option', 'Select Gender');
                    txt('signup-gender-male-option', 'Male');
                    txt('signup-gender-female-option', 'Female');
                    txt('signup-phone-label', 'Phone Number');
                    ph('signup-phone', 'Phone Number (e.g. 010-1234-5678)');
                    txt('signup-employee-number-label', 'Employee Number');
                    ph('signup-employee-number', 'Employee ID (8 digits)');
                    txt('signup-password-label', 'Password');
                    ph('signup-password', 'Password');
                    txt('signup-password-confirm-label', 'Confirm Password');
                    ph('signup-password-confirm', 'Confirm Password');
                    txt('signup-submit-btn', 'Sign Up');
                    txt('signup-cancel-btn', 'Cancel');
                    
                    txt('signup-last-name-use-label', 'Use');
                    txt('signup-middle-name-use-label', 'Use');
                }

                // 국적 변경 시 실시간 에러 메시지도 즉시 번역
                checkPasswordMatch();
                checkEmployeeNumber();
            };
            
            nationalitySelect.addEventListener('change', (e) => handleNationalityChange(e.target.value));
            
            // 체크박스 클릭 이벤트 핸들러 바인딩
            const lastNameUseCheckbox = document.getElementById('signup-last-name-use');
            const middleNameUseCheckbox = document.getElementById('signup-middle-name-use');

            if (lastNameUseCheckbox) {
                lastNameUseCheckbox.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        lastNameInput.disabled = false;
                        lastNameInput.style.backgroundColor = '#fff';
                        lastNameInput.focus();
                    } else {
                        lastNameInput.disabled = true;
                        lastNameInput.style.backgroundColor = '#eee';
                        lastNameInput.value = '';
                    }
                });
            }

            if (middleNameUseCheckbox && middleNameInput) {
                middleNameUseCheckbox.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        middleNameInput.disabled = false;
                        middleNameInput.style.backgroundColor = '#fff';
                        middleNameInput.focus();
                    } else {
                        middleNameInput.disabled = true;
                        middleNameInput.style.backgroundColor = '#eee';
                        middleNameInput.value = '';
                    }
                });
            }

            // 초기 로딩 시 상태 세팅
            handleNationalityChange(nationalitySelect.value);
        }

        const emailIdInput = document.getElementById('signup-email-id');
        const domainSelect = document.getElementById('signup-email-domain-select');
        const domainInput = document.getElementById('signup-email-domain');
        
        if (domainSelect && domainInput) {
            domainSelect.addEventListener('change', (e) => {
                if (e.target.value === 'custom') {
                    domainInput.value = '';
                    domainInput.readOnly = false;
                    domainInput.focus();
                } else {
                    domainInput.value = e.target.value;
                    domainInput.readOnly = true;
                }
            });
        }

        if (emailIdInput && domainInput && domainSelect) {
            const handleEmailIdInput = (e) => {
                const val = e.target.value.trim();
                if (val.includes('@')) {
                    const parts = val.split('@');
                    const idPart = parts[0];
                    const domainPart = parts[1] || '';
                    
                    emailIdInput.value = idPart;
                    domainInput.value = domainPart;
                    
                    let found = false;
                    for (let i = 0; i < domainSelect.options.length; i++) {
                        if (domainSelect.options[i].value === domainPart) {
                            domainSelect.value = domainPart;
                            domainInput.readOnly = true;
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                        domainSelect.value = 'custom';
                        domainInput.readOnly = false;
                    }
                }
            };
            emailIdInput.addEventListener('input', handleEmailIdInput);
            emailIdInput.addEventListener('change', handleEmailIdInput);
        }

        // 비밀번호 실시간 일치 검증 바인딩
        if (passwordInput && confirmInput && passwordError) {
            passwordInput.addEventListener('input', checkPasswordMatch);
            confirmInput.addEventListener('input', checkPasswordMatch);
        }

        // 사번 실시간 입력 제약 및 검증 (숫자만, 최대 8자리) 바인딩
        if (employeeNumberInput && employeeNumberError) {
            employeeNumberInput.addEventListener('input', (e) => {
                const val = e.target.value.replace(/[^\d]/g, '');
                e.target.value = val.slice(0, 8); // 최대 8글자 제한
                checkEmployeeNumber();
            });
        }

        // 중복 확인 상태 초기화
        state.isEmailChecked = false;
        state.checkedEmail = '';

        // 이메일 구성 요소가 변경되면 중복 확인 리셋
        const emailId = document.getElementById('signup-email-id');
        const emailDomain = document.getElementById('signup-email-domain');
        const emailDomainSelect = document.getElementById('signup-email-domain-select');
        const emailMsg = document.getElementById('signup-email-check-msg');

        const resetEmailCheck = () => {
            state.isEmailChecked = false;
            state.checkedEmail = '';
            if (emailMsg) {
                emailMsg.style.display = 'none';
                emailMsg.textContent = '';
            }
        };

        if (emailId) emailId.addEventListener('input', resetEmailCheck);
        if (emailDomain) emailDomain.addEventListener('input', resetEmailCheck);
        if (emailDomainSelect) emailDomainSelect.addEventListener('change', resetEmailCheck);
    },

    async renderPatients(params = {}) {
        const patients = await apis.getPatients(params);
        const html = await utils.loadTemplate('patients');
        if (state.currentPage !== '/patients') return;
        const app = document.getElementById('app');
        app.innerHTML = html;

        // 필드 값 복원
        const nameInput = document.getElementById('search-name');
        const genderSelect = document.getElementById('filter-gender');
        const minAgeInput = document.getElementById('filter-min-age');
        const maxAgeInput = document.getElementById('filter-max-age');

        if (nameInput && params.name) nameInput.value = params.name;
        if (genderSelect && params.gender) genderSelect.value = params.gender;
        if (minAgeInput && params.min_age) minAgeInput.value = params.min_age;
        if (maxAgeInput && params.max_age) maxAgeInput.value = params.max_age;
        
        const listBody = document.getElementById('patients-list');
        if (patients.length === 0) {
            listBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">검색 결과가 없습니다.</td></tr>';
            return;
        }
        listBody.innerHTML = patients.map(p => `
            <tr>
                <td>${p.id}</td>
                <td>${p.name}</td>
                <td>${p.age}</td>
                <td>${p.gender === 'male' ? '남성' : '여성'}</td>
                <td>${utils.formatPhoneNumber(p.phone_number)}</td>
                <td><button onclick="navigate('/patients/${p.id}')">상세보기</button></td>
            </tr>
        `).join('');
    },

    async renderPatientCreate() {
        const html = await utils.loadTemplate('patient-create');
        document.getElementById('app').innerHTML = html;
        
        const phoneInput = document.getElementById('phone_number');
        if (phoneInput) {
            phoneInput.addEventListener('input', (e) => utils.handlePhoneInput(e));
        }
    },

    async renderPatientDetail(patientId) {
        const patient = await apis.getPatient(patientId);
        const records = await apis.getPatientMedicalRecords(patientId);
        const html = await utils.loadTemplate('patient-detail');
        if (!state.currentPage.startsWith('/patients/')) return;
        const app = document.getElementById('app');
        app.innerHTML = html;
        
        // 환자 정보 표시
        document.getElementById('patient-name').innerText = `${patient.name} (${patient.gender === 'male' ? '남성' : '여성'})`;
        document.getElementById('patient-info').innerText = `나이: ${patient.age}세 | 연락처: ${utils.formatPhoneNumber(patient.phone_number)}`;
        
        // 수정 폼 초기값 설정
        document.getElementById('update-name').value = patient.name;
        document.getElementById('update-phone').value = utils.formatPhoneNumber(patient.phone_number);
        
        const updatePhoneInput = document.getElementById('update-phone');
        if (updatePhoneInput) {
            updatePhoneInput.addEventListener('input', (e) => utils.handlePhoneInput(e));
        }
        
        // 버튼 이벤트 바인딩
        document.getElementById('add-record-btn').onclick = () => navigate(`/patients/${patientId}/medical-records/create`);
        
        // 상세 페이지 전용 상태 (ID 저장)
        state.currentPatientId = patientId;

        const listBody = document.getElementById('records-list');
        listBody.innerHTML = records.map(r => `
            <tr>
                <td>${r.id}</td>
                <td>${r.chart_number}</td>
                <td>${r.symptoms}</td>
                <td>${new Date(r.created_at).toLocaleString()}</td>
                <td><button onclick="navigate('/medical-records/${r.id}')">상세보기</button></td>
            </tr>
        `).join('');
    },

    async renderRecordCreate(patientId) {
        const html = await utils.loadTemplate('record-create');
        const app = document.getElementById('app');
        app.innerHTML = html;
        
        const imageInput = document.getElementById('xray_image');
        const previewContainer = document.getElementById('image-preview-container');

        imageInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    previewContainer.innerHTML = `<img src="${event.target.result}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">`;
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.innerHTML = '<p>이미지 미리보기가 여기에 표시됩니다.</p>';
            }
        };

        document.getElementById('record-create-form').onsubmit = (e) => this.handleRecordCreate(e, patientId);
        document.getElementById('cancel-btn').onclick = () => navigate(`/patients/${patientId}`);
    },

    async renderRecordDetail(recordId) {
        const record = await apis.getMedicalRecord(recordId);
        const analyses = await apis.getMedicalRecordAnalyses(recordId);
        const html = await utils.loadTemplate('record-detail');
        const app = document.getElementById('app');
        app.innerHTML = html;
        
        document.getElementById('record-id').innerText = record.id;
        document.getElementById('chart-number').innerText = record.chart_number;
        document.getElementById('symptoms-text').innerText = record.symptoms;
        document.getElementById('created-at').innerText = new Date(record.created_at).toLocaleString();
        document.getElementById('xray-img').src = record.xray_image_url;
        
        document.getElementById('predict-btn').onclick = () => this.handlePredict(recordId);
        document.getElementById('back-to-patient-btn').onclick = () => navigate(`/patients/${record.patient_id}`);
        
        const analysisList = document.getElementById('analysis-list');
        if (analyses.length === 0) {
            analysisList.innerHTML = '<p>저장된 예측 결과가 없습니다.</p>';
        } else {
            analysisList.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>수행 일시</th>
                            <th>폐렴 여부</th>
                            <th>Confidence</th>
                            <th>사용 모델</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${analyses.map(a => `
                            <tr class="${a.is_pneumonia ? 'result-positive' : 'result-negative'}">
                                <td>${new Date(a.created_at).toLocaleString()}</td>
                                <td><strong>${a.is_pneumonia ? 'Positive' : 'Negative'}</strong></td>
                                <td>${a.confidence}%</td>
                                <td>${a.ai_model}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
    },

    async renderMyPage() {
        const html = await utils.loadTemplate('my-page');
        const app = document.getElementById('app');
        app.innerHTML = html;

        // 현재 사용자 정보 표시
        document.getElementById('me-email').innerText = state.user.email;
        document.getElementById('me-name-display').innerText = state.user.name;
        document.getElementById('me-department-display').innerText = state.user.department;
        document.getElementById('me-gender-display').innerText = state.user.gender === 'male' ? '남성' : '여성';
        document.getElementById('me-phone-display').innerText = utils.formatPhoneNumber(state.user.phone_number);
        document.getElementById('me-role-display').innerText = state.user.role;

        // 수정 폼 초기값 설정
        document.getElementById('update-me-department').value = state.user.department;
        document.getElementById('update-me-phone').value = utils.formatPhoneNumber(state.user.phone_number);
        
        const mePhoneInput = document.getElementById('update-me-phone');
        if (mePhoneInput) {
            mePhoneInput.addEventListener('input', (e) => utils.handlePhoneInput(e));
        }

        // 이벤트 바인딩
        document.getElementById('update-me-form').onsubmit = (e) => this.handleUpdateMe(e);
        document.getElementById('update-password-form').onsubmit = (e) => this.handleUpdatePassword(e);
        document.getElementById('delete-me-btn').onclick = () => this.handleDeleteMe();
    },

    async renderAdminUsers(params = {}) {
        const users = await apis.adminGetUsers(params);
        const html = await utils.loadTemplate('admin-users');
        if (state.currentPage !== '/admin/users') return;
        const app = document.getElementById('app');
        app.innerHTML = html;

        // 필드 값 복원
        const queryInput = document.getElementById('admin-search-query');
        const deptSelect = document.getElementById('admin-filter-dept');
        if (queryInput && params.query) queryInput.value = params.query;
        if (deptSelect && params.department) deptSelect.value = params.department;

        const listBody = document.getElementById('admin-users-list');
        if (users.length === 0) {
            listBody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">검색 결과가 없습니다.</td></tr>';
            return;
        }
        listBody.innerHTML = users.map(u => `
            <tr>
                <td>${u.id}</td>
                <td>${u.name}</td>
                <td>${u.email}</td>
                <td>${u.department}</td>
                <td>${utils.formatPhoneNumber(u.phone_number)}</td>
                <td>
                    <select onchange="pages.handleRoleUpdate(${u.id}, this.value)" ${u.id === state.user.id ? 'disabled' : ''}>
                        <option value="pending" ${u.role === 'pending' ? 'selected' : ''}>승인대기</option>
                        <option value="staff" ${u.role === 'staff' ? 'selected' : ''}>일반회원</option>
                        <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>관리자</option>
                    </select>
                </td>
                <td>${u.is_active ? '<span class="status-badge success">활성</span>' : '<span class="status-badge error">비활성</span>'}</td>
            </tr>
        `).join('');
    },

    // --- Event Handlers ---

    handleAdminSearch() {
        const query = document.getElementById('admin-search-query').value;
        const department = document.getElementById('admin-filter-dept').value;
        
        const params = new URLSearchParams();
        if (query) params.set('query', query);
        if (department) params.set('department', department);
        
        const queryString = params.toString();
        const path = '/admin/users' + (queryString ? '?' + queryString : '');
        navigate(path);
    },

    resetAdminSearch() {
        navigate('/admin/users');
    },

    async handleRoleUpdate(userId, newRole) {
        try {
            await apis.adminUpdateUserRole({ user_id: userId, new_role: newRole });
            utils.showAlert('권한이 변경되었습니다.', 'success');
            this.handleAdminSearch();
        } catch (err) {
            utils.showAlert(`권한 변경 실패: ${err.message}`, 'error');
        }
    },

    async handleUpdateMe(e) {
        e.preventDefault();
        const data = {
            department: document.getElementById('update-me-department').value,
            phone_number: document.getElementById('update-me-phone').value.replace(/[^\d]/g, '')
        };

        try {
            await apis.updateMe(data);
            utils.showAlert('회원 정보가 수정되었습니다.', 'success');
            await checkAuth(); // state 갱신 (app.js)
            this.renderMyPage();
        } catch (err) {
            let msg = err.message;
            if (err.status === 500) msg = '잠시 후 다시시도해주세요.';
            utils.showAlert(msg, 'error', '수정 실패');
        }
    },

    async handleUpdatePassword(e) {
        e.preventDefault();
        const data = {
            current_password: document.getElementById('old-password').value,
            new_password: document.getElementById('new-password').value
        };

        try {
            await apis.updatePassword(data);
            utils.showAlert('비밀번호가 변경되었습니다.', 'success');
            e.target.reset();
        } catch (err) {
            let msg = err.message;
            if (err.status === 400) {
                msg = '비밀번호는 "대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다."';
            } else if (err.status === 500) {
                msg = '잠시 후 다시시도해주세요.';
            }
            utils.showAlert(msg, 'error', '비밀번호 변경 실패');
        }
    },

    async handleDeleteMe() {
        if (!confirm('정말로 탈퇴하시겠습니까? 모든 데이터가 삭제됩니다.')) return;

        try {
            await apis.deleteMe();
            utils.showAlert('탈퇴 처리가 완료되었습니다.', 'success');
            logout(); // (app.js)
        } catch (err) {
            utils.showAlert(`탈퇴 처리 실패: ${err.message}`, 'error');
        }
    },

    async handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        await login(email, password); // (app.js)
    },

    async handleEmailCheck(e) {
        if (e) e.preventDefault();
        
        const nationality = document.getElementById('signup-nationality').value;
        const isKorean = nationality === 'korean';
        
        const emailId = document.getElementById('signup-email-id').value.trim();
        const emailDomain = document.getElementById('signup-email-domain').value.trim();
        
        if (!emailId || !emailDomain) {
            utils.showAlert(
                isKorean ? '이메일 아이디와 도메인을 모두 입력해 주세요.' : 'Please enter both email ID and domain.',
                'error',
                isKorean ? '검증 실패' : 'Validation Failed'
            );
            return;
        }
        
        const email = `${emailId}@${emailDomain}`;
        const emailMsg = document.getElementById('signup-email-check-msg');
        
        try {
            const data = await apis.checkEmail(email);
            state.isEmailChecked = true;
            state.checkedEmail = email;
            
            if (emailMsg) {
                emailMsg.style.display = 'block';
                emailMsg.style.color = 'var(--secondary-color)';
                emailMsg.textContent = isKorean ? '사용 가능한 이메일입니다.' : 'This email is available.';
            }
        } catch (err) {
            state.isEmailChecked = false;
            state.checkedEmail = '';
            
            if (emailMsg) {
                emailMsg.style.display = 'block';
                emailMsg.style.color = 'var(--danger-color)';
                emailMsg.textContent = err.message || (isKorean ? '중복 확인에 실패했습니다.' : 'Failed to verify email.');
            }
        }
    },

    async handleSignup(e) {
        e.preventDefault();

        const nationality = document.getElementById('signup-nationality').value;
        const isKorean = nationality === 'korean';

        const emailId = document.getElementById('signup-email-id').value.trim();
        const emailDomain = document.getElementById('signup-email-domain').value.trim();
        const email = `${emailId}@${emailDomain}`;

        if (!state.isEmailChecked || state.checkedEmail !== email) {
            utils.showAlert(
                isKorean ? '이메일 중복 확인을 해주세요.' : 'Please check email duplication.',
                'error',
                isKorean ? '검증 실패' : 'Validation Failed'
            );
            return;
        }

        const password = document.getElementById('signup-password').value;
        const confirmPassword = document.getElementById('signup-password-confirm').value;

        if (password !== confirmPassword) {
            utils.showAlert(
                isKorean ? '비밀번호가 일치하지 않습니다.' : 'Passwords do not match.',
                'error',
                isKorean ? '검증 실패' : 'Validation Failed'
            );
            return;
        }

        const employeeNumber = document.getElementById('signup-employee-number').value.trim();
        if (!/^\d{8}$/.test(employeeNumber)) {
            utils.showAlert(
                isKorean ? '사번은 8자리 숫자여야 합니다.' : 'Employee ID must be an 8-digit number.',
                'error',
                isKorean ? '검증 실패' : 'Validation Failed'
            );
            return;
        }

        const lastName = document.getElementById('signup-last-name').value.trim();
        const firstName = document.getElementById('signup-first-name').value.trim();
        const middleName = document.getElementById('signup-middle-name').value.trim();

        if (isKorean) {
            if (!lastName) {
                utils.showAlert('성은 필수 입력 항목입니다.', 'error', '검증 실패');
                return;
            }
            if (!firstName) {
                utils.showAlert('이름은 필수 입력 항목입니다.', 'error', '검증 실패');
                return;
            }
        } else {
            if (!firstName) {
                utils.showAlert('First Name is required.', 'error', 'Validation Failed');
                return;
            }
        }

        const userData = {
            email: email,
            nationality: nationality,
            last_name: lastName || null,
            first_name: firstName,
            middle_name: middleName || null,
            department: document.getElementById('signup-department').value,
            gender: document.getElementById('signup-gender').value,
            phone_number: document.getElementById('signup-phone').value.replace(/[^\d]/g, ''),
            password: password,
            employee_number: employeeNumber
        };

        try {
            await apis.signup(userData);
            utils.showAlert(
                isKorean ? '회원가입이 완료되었습니다. 로그인해주세요.' : 'Sign up completed. Please log in.',
                'success'
            );
            navigate('/login');
        } catch (err) {
            let msg = err.message;
            if (err.status === 400) {
                if (msg.includes('비밀번호') || msg.includes('password')) {
                    msg = isKorean
                        ? '비밀번호는 "대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다."'
                        : 'Password must be 8-20 characters long and include uppercase, lowercase, numbers, and special characters.';
                } else if (msg.includes('사번') || msg.includes('employee_number') || msg.includes('employee number') || msg.includes('employee')) {
                    if (msg.includes('이미 가입된') || msg.includes('already registered') || msg.includes('already exists') || msg.includes('중복')) {
                        msg = isKorean ? '이미 가입된 사번입니다.' : 'This Employee ID is already registered.';
                    } else {
                        msg = isKorean ? '사번은 8자리 숫자여야 합니다.' : 'Employee ID must be an 8-digit number.';
                    }
                } else if (msg.includes('이메일') || msg.includes('email')) {
                    if (msg.includes('이미 등록된') || msg.includes('already registered') || msg.includes('이미 가입된')) {
                        msg = isKorean ? '이미 등록된 이메일입니다.' : 'This email is already registered.';
                    } else {
                        msg = isKorean ? '올바른 이메일 형식이 아닙니다.' : 'Invalid email format.';
                    }
                } else if (msg.includes('나이') || msg.includes('age')) {
                    msg = isKorean ? '나이는 최소 14세 이상이어야 합니다.' : 'Age must be 14 or older.';
                }
            } else if (err.status === 500) {
                msg = isKorean ? '잠시 후 다시시도해주세요.' : 'Please try again later.';
            }
            utils.showAlert(msg, 'error', isKorean ? '가입 실패' : 'Registration Failed');
        }
    },

    async handlePatientCreate(e) {
        e.preventDefault();
        const patientData = {
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            phone_number: document.getElementById('phone_number').value.replace(/[^\d]/g, '')
        };
        
        try {
            await apis.createPatient(patientData);
            utils.showAlert('환자가 등록되었습니다.', 'success');
            navigate('/patients');
        } catch (err) {
            utils.showAlert(`환자 등록 실패: ${err.message}`, 'error');
        }
    },

    handleSearch() {
        const name = document.getElementById('search-name').value;
        const gender = document.getElementById('filter-gender').value;
        const min_age = document.getElementById('filter-min-age').value;
        const max_age = document.getElementById('filter-max-age').value;

        const params = new URLSearchParams();
        if (name) params.set('name', name);
        if (gender) params.set('gender', gender);
        if (min_age) params.set('min_age', min_age);
        if (max_age) params.set('max_age', max_age);

        const queryString = params.toString();
        const path = '/patients' + (queryString ? '?' + queryString : '');
        navigate(path);
    },

    resetSearch() {
        navigate('/patients');
    },

    async handleRecordCreate(e, patientId) {
        e.preventDefault();
        const formData = new FormData();
        formData.append('patient_id', patientId);
        formData.append('chart_number', document.getElementById('chart_number').value);
        formData.append('symptoms', document.getElementById('symptoms').value);
        formData.append('xray_image', document.getElementById('xray_image').files[0]);

        try {
            await apis.createMedicalRecord(formData);
            utils.showAlert('진료 기록이 등록되었습니다.', 'success');
            navigate(`/patients/${patientId}`);
        } catch (err) {
            utils.showAlert(`진료 기록 등록 실패: ${err.message}`, 'error');
        }
    },

    openUpdateModal() {
        document.getElementById('update-modal').classList.add('show');
    },

    closeUpdateModal() {
        document.getElementById('update-modal').classList.remove('show');
    },

    async handlePatientUpdate(e) {
        e.preventDefault();
        const patientId = state.currentPatientId;
        const updateData = {
            name: document.getElementById('update-name').value,
            phone_number: document.getElementById('update-phone').value.replace(/[^\d]/g, '')
        };

        try {
            await apis.updatePatient(patientId, updateData);
            utils.showAlert('환자 정보가 수정되었습니다.', 'success');
            this.closeUpdateModal();
            this.renderPatientDetail(patientId);
        } catch (err) {
            utils.showAlert(`환자 정보 수정 실패: ${err.message}`, 'error');
        }
    },

    confirmDeletePatient() {
        document.getElementById('delete-modal').classList.add('show');
    },

    closeDeleteModal() {
        document.getElementById('delete-modal').classList.remove('show');
    },

    async handlePatientDelete() {
        const patientId = state.currentPatientId;
        try {
            await apis.deletePatient(patientId);
            utils.showAlert('환자 정보와 관련 데이터가 모두 삭제되었습니다.', 'success');
            this.closeDeleteModal();
            navigate('/patients');
        } catch (err) {
            utils.showAlert(`환자 삭제 실패: ${err.message}`, 'error');
        }
    },

    async handlePredict(recordId) {
        try {
            await apis.predictPneumonia(recordId);
            utils.showAlert('AI 예측이 완료되었습니다.', 'success');
            navigate(`/medical-records/${recordId}`, false);
        } catch (err) {
            utils.showAlert(`AI 예측 실패: ${err.message}`, 'error');
        }
    }
};
