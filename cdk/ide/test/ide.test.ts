import * as cdk from "aws-cdk-lib";
import * as Ide from "../lib/ide-stack";

test("SQS Queue and SNS Topic Created", () => {
  const app = new cdk.App();
  // WHEN
  const stack = new Ide.FoundationStack(app, "MyTestStack", {
    sourceZipFile: "workshop-stack-app.zip",
    sourceZipFileChecksum: "",
  });
  // THEN
  const actual = JSON.stringify(
    app.synth().getStackArtifact(stack.artifactId).template
  );
  expect(actual).toContain("AWS::SQS::Queue");
  expect(actual).toContain("AWS::SNS::Topic");
});
