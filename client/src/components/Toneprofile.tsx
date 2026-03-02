import Button from "@/components/Button";

interface ToneProfileModalProps {
  hasProfile?: boolean;
}

export const ToneProfileModal = ({
  hasProfile = true,
}: ToneProfileModalProps) => {
  if (hasProfile) {
    // profile exists
    return (
      <>
        <p className="text-5xl not-italic font-bold text-center">
          We found your tone profile!
        </p>
        <p className="mt-8 text-center text-[2.50rem] leading-none not-italic font-medium">
          Continue with it or make a few tweaks
          <br />
          before you start
        </p>
        <div className="flex justify-center mt-6 gap-[37px]">
          <Button variant="secondary" size="md">
            Update
            <br />
            via Survey
          </Button>
          <Button variant="primary" size="md">
            Update
            <br />
            via Document Upload
          </Button>
        </div>
      </>
    );
  }

  // profile does not exist
  return (
    <>
      <p className="text-5xl not-italic font-bold text-center">
        Create your tone profile
      </p>
      <p className="mt-8 text-center text-[2.50rem] leading-none not-italic font-medium">
        Let's create a personalized tone profile to get started
      </p>
      <div className="flex justify-center mt-6 gap-[37px]">
        <Button variant="secondary" size="md">
          Start Survey
        </Button>
        <Button variant="primary" size="md">
          Upload Document
        </Button>
      </div>
    </>
  );
};
