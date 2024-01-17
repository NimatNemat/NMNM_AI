# NMNM_AI  
<br>  

## 소개
니맛내맛 프로젝트는 사용자의 식당 평가를 기반으로 식당을 추천해주는 시스템입니다. 사용자는 자신이 선호하는 식당 그룹에 따른 추천, 사용자의 식당 평가에 따른 개인 별 추천, 마지막으로 함께 먹을 사람을 추가하여 함께 먹는 인원 모두의 취향에 맞는 식당을 추천해줄 수 있는 함께 먹기 추천 방식을 제공합니다.  
  
<br>  

## [프로젝트 소개 영상]  
https://www.youtube.com/watch?v=uyXTeoq9q4k&list=PLMr9Py20DqB8j8IIyIVHf9FBwlVhQTntM&index=8  

<br>  

## [구성]
추천 로직과 관련한 코드들은 Recommend 폴더에 넣어두었습니다.  
데이터베이스 업데이트 로직과 관련한 코드들은 TableUpdate 폴더에 넣어두었습니다.  

<br>  

## [프로젝트 보고서]
https://github.com/NimatNemat/NMNM_AI/blob/main/캡스톤_프로젝트_결과보고서.pdf

<br>

## [핵심 구현 코드]
그룹 별 추천(1차 추천) : https://github.com/NimatNemat/NMNM_AI/blob/main/Recommend/1stR.py  
사용자 별 추천(2차 추천) : https://github.com/NimatNemat/NMNM_AI/blob/main/Recommend/2ndR.py  
함께 먹기 추천(3차 추천) : https://github.com/NimatNemat/NMNM_AI/blob/main/Recommend/3ndRecommendAPI2.py  
