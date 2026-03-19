const artTemplate = require("art-template");
const { default: chalk } = require("chalk");
const { Command } = require("commander");
const fs = require("fs/promises");
const moment = require("moment");
const path = require("path");

async function exists(p) {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  const cmd = new Command();
  cmd.requiredOption(
    "-p, --path <string>",
    "笔记路径，第一个路径名是大类，如：python/notation",
  );
  cmd.option("-f, --force", "是否强行创建（覆盖已存在文件）", false); // 不加<bool> 表示这是一个flag
  cmd.parse();
  const opts = cmd.opts();
  const post_path = opts.path;

  const create_time = moment();
  const targetPath = path.resolve(
    `./docs/${create_time.format("YYYY")}/${post_path}/`,
  );
  const targetFile = path.join(targetPath, "index.md");

  if (!opts.force && (await exists(targetFile))) {
    console.log(chalk.red.bold("文件已存在，添加-f 强行创建"));
  }

  await fs.mkdir(targetPath, { recursive: true }, (err) => {
    if (err) console.log(chalk.red.bold(err));
  });

  const md = artTemplate(__dirname + "/post-template.art", {
    time_stamp: create_time.format("YYYY-MM-DD HH:mm:ss"),
    tag: "python",
  });

  fs.writeFile(targetFile, md, (err) => {
    if (err) console.log(chalk.red.bold(err));
  });
  console.log(
    chalk.green.bold(`文件创建成功： ${path.relative(__dirname, targetFile)}`),
  );
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
