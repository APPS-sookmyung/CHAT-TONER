import { useNavigate } from "react-router-dom";
import { PATH } from "@/constants/paths"; // 1. 경로 상수를 import
import Button from "../components/Atoms/Button";

// 2. 가독성을 위해 텍스트 데이터를 컴포넌트 밖으로 분리
const FEATURES = [
  {
    text: "Standardize team communication with ",
    highlight: "style profiles",
  },
  {
    text: "Reduce editing overhead with ",
    highlight: "automated tone checks",
  },
  {
    text: "Build trust with ",
    highlight: "consistent brand voice",
  },
];

const LandingPage = () => {
  // 3. 네비게이션 함수를 깔끔하게 처리
  const navigate = useNavigate();
  const handleStartClick = () => {
    navigate(PATH.CHOICE); // 'Get Started' 클릭 시 /choice 페이지로 이동
  };

  return (
    // 4. <main> 태그로 시맨틱 의미 부여, flex로 전체를 중앙 정렬
    <main className="flex flex-col items-center justify-center min-h-screen px-4">
      {/* 5. <h1> 태그와 <p> 태그는 text-center를 명시 */}
      <h1 className="mb-12 font-medium leading-[95px] text-center text-black text-8xl">
        An AI-powered tool to <br />
        <span className="text-primary">unify communication</span>
        <br />
        <span className="text-primary">styles</span> across your team
      </h1>

      {/* 6. gap-12 (48px)는 mb-12로, 122px는 mb-[122px]로 적용 */}
      <div className="mb-[122px] flex flex-col gap-1.5 text-center text-3xl text-text-secondary">
        {/* 7. 데이터를 map으로 렌더링하여 JSX를 깔끔하게 유지 */}
        {FEATURES.map((feature) => (
          <p key={feature.highlight}>
            {feature.text}
            <span className="text-primary">{feature.highlight}</span>
          </p>
        ))}
      </div>

      <Button variant="primary" size="lg" onClick={handleStartClick}>
        Get Started
      </Button>
    </main>
  );
};

export default LandingPage;
