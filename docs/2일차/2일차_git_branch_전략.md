# 2일차 Git Branch 전략

## 1. 학습 목표

이번 학습의 목표는 Git 협업에서 자주 사용되는 브랜치 전략을 이해하고, 우리 팀 프로젝트에 맞는 브랜치 운영 방식을 정리하는 것이다. 특히 `Git Flow`, `GitHub Flow`, 그리고 우리 팀이 사용하기로 한 `GitHub Flow 변형 전략`을 비교한다.

---

## 2. Git Branch 전략이 필요한 이유

Git Branch 전략이란 여러 개발자가 하나의 저장소에서 협업할 때, 브랜치를 어떤 기준으로 만들고 병합할지 정한 규칙이다.

브랜치 전략이 필요한 이유는 다음과 같다.

- 여러 사람이 동시에 작업해도 서로의 코드에 직접적인 영향을 덜 준다.
- 기능별, 이슈별로 작업 단위를 분리할 수 있다.
- Pull Request를 통해 코드 리뷰와 변경 이력 확인이 쉬워진다.
- 문제가 생겼을 때 특정 작업 단위로 되돌리거나 수정하기 쉽다.
- 배포용 코드와 개발 중인 코드를 분리하여 안정성을 높일 수 있다.

즉, 브랜치 전략은 단순히 브랜치를 많이 만드는 규칙이 아니라, 팀 협업과 배포 안정성을 위한 작업 흐름이다.

---

## 3. Git Flow

## 3-1. 개념

`Git Flow`는 비교적 체계적이고 엄격한 브랜치 전략이다. 배포 주기가 명확하거나, 여러 기능을 모아서 테스트한 뒤 정해진 시점에 배포하는 프로젝트에 적합하다.

기본 구조는 다음과 같다.

```text
main(master)  ←  release  ←  develop  ←  feature/기능명
      ↑
   hotfix/긴급수정
```

## 3-2. 주요 브랜치 역할

| 브랜치 | 역할 |
|---|---|
| `main` 또는 `master` | 실제 배포 가능한 최종 코드가 있는 브랜치 |
| `develop` | 다음 배포 버전을 위해 개발된 기능을 통합하는 브랜치 |
| `feature/기능명` | 개별 기능을 개발하는 브랜치 |
| `release` | 배포 전 QA, 테스트, 버그 수정을 진행하는 브랜치 |
| `hotfix` | 배포 후 운영 환경에서 발생한 긴급 버그를 수정하는 브랜치 |

## 3-3. 작업 흐름

1. `develop` 브랜치에서 `feature/기능명` 브랜치를 생성한다.
2. 각 개발자는 `feature` 브랜치에서 기능을 개발한다.
3. 기능 개발이 끝나면 Pull Request를 통해 `develop` 브랜치로 병합한다.
4. 여러 기능이 모이면 `develop`에서 `release` 브랜치를 생성한다.
5. `release` 브랜치에서 배포 전 테스트와 버그 수정을 진행한다.
6. 배포 준비가 끝나면 `release`를 `main`에 병합한다.
7. 배포 후 긴급 수정이 필요하면 `main`에서 `hotfix` 브랜치를 생성해 수정한다.
8. `hotfix` 수정 내용은 `main`뿐 아니라 `develop`에도 반영하여 브랜치 간 차이를 줄인다.

## 3-4. 장점

- 배포 코드와 개발 코드를 명확히 분리할 수 있다.
- `release`, `hotfix` 브랜치를 통해 배포 전후의 안정성을 확보하기 좋다.
- 대규모 프로젝트, 정기 배포 프로젝트에 적합하다.
- 버전 관리와 롤백 흐름을 체계적으로 운영할 수 있다.

## 3-5. 단점

- 브랜치 종류가 많아 초보자에게 복잡할 수 있다.
- 작은 프로젝트에서는 과정이 과하게 느껴질 수 있다.
- 빠른 기능 배포가 필요한 프로젝트에서는 절차가 무겁게 느껴질 수 있다.

## 3-6. 적합한 상황

- 배포 일정이 정해져 있는 프로젝트
- QA 단계가 필요한 프로젝트
- 운영 중인 서비스에서 긴급 수정 대응이 필요한 경우
- 팀 규모가 크거나 기능 개발이 병렬로 많이 진행되는 경우

---

## 4. GitHub Flow

## 4-1. 개념

`GitHub Flow`는 Git Flow보다 단순한 브랜치 전략이다. 기본적으로 `main` 브랜치와 `feature` 브랜치만 사용한다.

기본 구조는 다음과 같다.

```text
main  ←  feature/기능명
```

`main` 브랜치는 항상 배포 가능한 상태를 유지하고, 새로운 기능이나 버그 수정은 `main`에서 분기한 별도 브랜치에서 작업한다. 작업이 끝나면 Pull Request를 열어 리뷰를 받고, 승인 후 `main`에 병합한다.

## 4-2. 주요 브랜치 역할

| 브랜치 | 역할 |
|---|---|
| `main` | 항상 배포 가능한 안정적인 코드가 있는 브랜치 |
| `feature/기능명` | 새로운 기능 개발 또는 버그 수정을 진행하는 브랜치 |

## 4-3. 작업 흐름

1. `main` 브랜치를 최신 상태로 유지한다.
2. 새로운 작업이 필요하면 `main`에서 `feature/기능명` 브랜치를 생성한다.
3. `feature` 브랜치에서 작업하고 커밋한다.
4. 작업 중간에도 원격 저장소에 자주 push하여 작업 내용을 공유한다.
5. 기능이 완성되었거나 리뷰가 필요하면 Pull Request를 생성한다.
6. 팀원이 Pull Request에서 코드 리뷰와 의견을 남긴다.
7. 피드백을 반영한 뒤 승인되면 `main`에 병합한다.
8. 병합 후 해당 `feature` 브랜치는 삭제한다.

## 4-4. 장점

- 구조가 단순해서 초보자도 이해하기 쉽다.
- 빠른 개발과 빠른 배포에 적합하다.
- Pull Request 중심으로 코드 리뷰를 진행하기 좋다.
- 브랜치 수가 적어 관리 부담이 적다.

## 4-5. 단점

- `main`에 바로 병합되므로 테스트와 리뷰가 부족하면 위험하다.
- 여러 기능을 한 번에 모아서 검토하기 어렵다.
- 배포 전 별도 QA 단계가 필요한 프로젝트에는 부족할 수 있다.

## 4-6. 적합한 상황

- 소규모 팀 프로젝트
- 빠른 기능 반영이 중요한 프로젝트
- 지속적 배포 환경이 있는 프로젝트
- 브랜치 전략을 처음 배우는 팀

---

## 5. Git Flow와 GitHub Flow 비교

| 비교 항목 | Git Flow | GitHub Flow |
|---|---|---|
| 구조 | 복잡함 | 단순함 |
| 주요 브랜치 | `main`, `develop`, `feature`, `release`, `hotfix` | `main`, `feature` |
| 개발 통합 위치 | `develop` | `main` |
| 배포 준비 | `release` 브랜치에서 진행 | 별도 release 브랜치 없이 PR 후 바로 병합 |
| 긴급 수정 | `hotfix` 브랜치 사용 | 일반 feature 브랜치처럼 처리 가능 |
| 장점 | 안정적, 체계적, 배포 관리에 유리 | 쉽고 빠름, 초보자에게 적합 |
| 단점 | 초보자에게 복잡함 | main 안정성 관리가 중요함 |
| 적합한 프로젝트 | 대규모, 정기 배포, QA 필요 | 소규모, 빠른 개발, 지속 배포 |

---

## 6. 우리 팀의 브랜치 전략: GitHub Flow 변형

## 6-1. 선택한 구조

우리 팀은 기본 GitHub Flow를 그대로 사용하지 않고, 중간 통합 브랜치인 `dev`를 추가한 변형 전략을 사용하기로 했다.

```text
main  ←  dev  ←  feature/기능명
```

각 브랜치의 의미는 다음과 같다.

| 브랜치 | 역할 |
|---|---|
| `main` | 최종 완성본만 반영하는 브랜치 |
| `dev` | 팀원들의 작업물을 먼저 합치는 중간 통합 브랜치 |
| `feature/기능명` | 각자 맡은 기능을 개발하는 개인 작업 브랜치 |

## 6-2. 왜 GitHub Flow를 변형했는가?

기본 GitHub Flow는 `main` 브랜치에서 바로 `feature` 브랜치를 만들고, 작업 완료 후 Pull Request를 통해 `main`에 병합한다.

하지만 우리 팀은 다음과 같은 이유로 `dev` 브랜치를 추가했다.

- 팀원들이 Git과 GitHub 협업에 익숙하지 않은 초보자 팀이다.
- 과제 진행 중 여러 기능을 한 번에 모아서 확인해야 한다.
- 완성되지 않은 기능이 `main`에 바로 들어가는 것을 막고 싶다.
- `main`은 최종 제출 가능한 안정적인 상태로 유지하고 싶다.
- `dev`에서 먼저 충돌, 오류, 화면 깨짐 등을 확인한 뒤 `main`에 반영하는 편이 안전하다.

즉, 우리 팀 전략은 GitHub Flow의 단순함을 유지하면서도, Git Flow의 `develop` 브랜치 개념을 일부 가져온 방식이다.

## 6-3. 우리 팀 작업 흐름

1. 팀장은 `main` 브랜치에서 `dev` 브랜치를 생성한다.
2. 팀원은 `dev` 브랜치를 기준으로 `feature/기능명` 브랜치를 생성한다.
3. 각자 맡은 기능을 `feature` 브랜치에서 개발한다.
4. 작업이 끝나면 `feature` 브랜치를 원격 저장소에 push한다.
5. GitHub에서 `feature/기능명` → `dev` 방향으로 Pull Request를 생성한다.
6. 팀원 또는 팀장이 Pull Request를 확인하고 코드 리뷰를 진행한다.
7. 문제가 없으면 `dev`에 병합한다.
8. 여러 기능이 `dev`에 모이면 전체 실행 테스트를 진행한다.
9. 최종 확인 후 `dev` → `main` 방향으로 Pull Request를 생성한다.
10. 최종 검토 후 `main`에 병합한다.

## 6-4. 우리 팀 브랜치 예시

```text
main
└── dev
    ├── feature/header-ui
    ├── feature/login-page
    ├── feature/board-list
    └── feature/footer-style
```

기능 이름이 아직 정해지지 않은 경우에는 다음처럼 일반적인 이름을 사용할 수 있다.

- `feature/layout`
- `feature/main-page`
- `feature/nav-bar`
- `feature/form-ui`
- `feature/api-connect`
- `feature/style-fix`

## 6-5. 우리 팀 규칙 제안

### main 브랜치 규칙

- 직접 push하지 않는다.
- 최종 완성본만 병합한다.
- `dev`에서 충분히 확인된 코드만 Pull Request로 병합한다.
- 제출용, 발표용, 최종 배포용 브랜치로 생각한다.

### dev 브랜치 규칙

- 팀원들의 기능을 먼저 합치는 브랜치이다.
- 기능별 Pull Request의 도착지는 기본적으로 `dev`이다.
- `dev`에 병합하기 전 최소 1명 이상이 확인한다.
- 병합 후 전체 실행이 깨지지 않는지 확인한다.

### feature 브랜치 규칙

- 하나의 브랜치에는 하나의 기능만 작업한다.
- 브랜치 이름은 기능을 알 수 있게 작성한다.
- 작업 전에는 항상 `dev`를 최신 상태로 pull한다.
- 작업이 끝나면 `feature` → `dev` Pull Request를 생성한다.
- 병합이 끝난 feature 브랜치는 삭제한다.

---

## 7. 기본 명령어 예시

## 7-1. dev 브랜치 최신화

```bash
git switch dev
git pull origin dev
```

## 7-2. feature 브랜치 생성

```bash
git switch dev
git pull origin dev
git switch -c feature/기능명
```

예시:

```bash
git switch -c feature/header-ui
```

## 7-3. 작업 후 커밋과 push

```bash
git status
git add .
git commit -m "feat: 헤더 UI 구현"
git push origin feature/header-ui
```

## 7-4. Pull Request 방향

```text
feature/기능명  →  dev
```

최종 완성 시:

```text
dev  →  main
```

---

## 8. 정리

브랜치 전략은 프로젝트 규모와 팀 상황에 따라 다르게 선택해야 한다.

`Git Flow`는 안정성과 체계적인 배포 관리에 강점이 있지만, 초보자 팀이나 작은 프로젝트에는 복잡할 수 있다. `GitHub Flow`는 단순하고 빠르지만, `main` 브랜치에 바로 병합되므로 리뷰와 테스트가 부족하면 위험할 수 있다.

우리 팀은 초보자 팀이고 여러 기능을 한 번에 검토해야 하므로, 기본 GitHub Flow에 `dev` 브랜치를 추가한 변형 전략을 사용하는 것이 적절하다. 이 방식은 `main`을 안정적으로 유지하면서도, 팀원들이 각자 `feature` 브랜치에서 독립적으로 개발하고 `dev`에서 먼저 통합 테스트를 할 수 있다는 장점이 있다.

따라서 우리 팀의 최종 브랜치 전략은 다음과 같이 정리할 수 있다.

```text
main = 최종 완성본
 dev = 중간 통합 및 테스트
 feature/기능명 = 개인 기능 개발
```

---

## 9. 참고 자료

- 주니어 개발자의 현업에서 배운 Git Flow: https://velog.io/@myoungji-kim/git-flow
- Git Branch 전략 비교 - Git Flow vs GitHub Flow: https://devocean.sk.com/blog/techBoardDetail.do?ID=165571&boardType=techBlog
- 사례로 이해하는 GitHub Flow: https://www.heropy.dev/p/6hdJi6
- GitHub Docs - GitHub Flow: https://docs.github.com/get-started/quickstart/github-flow
- GitHub Flow 원문 설명: https://githubflow.github.io/
